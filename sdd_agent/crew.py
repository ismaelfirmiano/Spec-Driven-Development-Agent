"""Experimento SDD x Linguagem Natural com CrewAI + Gemini.

- SDD:     especificação -> analisar (plano) -> implementar
- Natural: pedido em linguagem natural -> gerar_natural
O mesmo agente "desenvolvedor", com as mesmas regras técnicas, implementa as
duas versões; a revisão (--revisar) é opcional e, se ligada, vale para ambas.
A comparação é feita às cegas contra uma especificação de referência comum.
"""

from __future__ import annotations

import os
import random
import posixpath
import re
import time
from functools import lru_cache
from pathlib import Path, PurePosixPath

import yaml
from crewai import LLM, Agent, Crew, Process, Task
from pydantic import BaseModel, Field

from .validacao import validar

CONFIG_DIR = Path(__file__).parent / "config"
MODELO_PADRAO = "gemini/gemini-3.8-flash"
RESERVA_PADRAO = "gemini/gemini-3.5-flash-lite,gemini/gemini-3.1-flash-lite"
ESPERAS_SEGUNDOS = (1,)
MAX_TOKENS_PADRAO = 32768  # apps de specs grandes não cabem em 8k tokens
MAX_ESPECIFICACAO_CHARS = 100_000


# ---------------------------------------------------------------------------
# Saída estruturada (garante que recebemos arquivos, não prosa)
# ---------------------------------------------------------------------------
class ArquivoGerado(BaseModel):
    caminho: str = Field(description="Caminho relativo, ex.: index.html ou css/style.css")
    conteudo: str = Field(description="Conteúdo completo do arquivo")


class ProgramaGerado(BaseModel):
    arquivos: list[ArquivoGerado]
    entrada: str = Field(default="index.html", description="Arquivo a abrir no navegador")
    relatorio: str = Field(default="", description="Rastreabilidade requisito -> código, em Markdown")


class RelatorioGerado(BaseModel):
    relatorio: str = Field(description="Relatório comparativo em Markdown")


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _carregar_yaml(nome: str) -> dict:
    with open(CONFIG_DIR / nome, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _regras_tecnicas() -> str:
    return (CONFIG_DIR / "regras_tecnicas.md").read_text(encoding="utf-8").strip()


def _preencher(texto: str, valores: dict[str, str]) -> str:
    valores = {"REGRAS_TECNICAS": _regras_tecnicas(), **valores}
    for chave, valor in valores.items():
        texto = texto.replace(f"[[{chave}]]", valor)
    return texto


def modelos_candidatos(modelo: str | None = None) -> list[str]:
    principal = modelo or os.getenv("SDD_MODEL", MODELO_PADRAO)
    reserva = os.getenv("SDD_MODELOS_RESERVA", RESERVA_PADRAO)
    lista = [principal] + [m.strip() for m in reserva.split(",") if m.strip()]
    return list(dict.fromkeys(lista))  # remove repetidos mantendo a ordem


def criar_llm(modelo: str) -> LLM:
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        raise RuntimeError("Defina GEMINI_API_KEY no arquivo .env")
    try:
        max_tokens = int(os.getenv("SDD_MAX_TOKENS", MAX_TOKENS_PADRAO))
    except ValueError as erro:
        raise RuntimeError("SDD_MAX_TOKENS deve ser um número inteiro") from erro
    if max_tokens < 1:
        raise RuntimeError("SDD_MAX_TOKENS deve ser maior que zero")
    return LLM(model=modelo, temperature=0.2, max_tokens=max_tokens)


def _tipo_erro(erro: Exception) -> str:
    """'transitorio' (vale repetir), 'modelo' (trocar de modelo) ou 'outro'."""
    texto = str(erro).lower()
    modelos_incompativeis = (
        "function calling is not enabled",
        "function calling is not supported",
        "tool calling is not supported",
        "does not support function calling",
        "model not found",
        "model is not supported",
        "unsupported model",
    )
    if any(t in texto for t in modelos_incompativeis):
        return "modelo"
    transitorios = (
        "503", "unavailable", "429", "resource_exhausted", "high demand", "overloaded",
        "none or empty", "não retornou nenhum arquivo", "arquivos=[]", "500", "internal",
        "timed out", "timeout",
        "arquivo vazio", "arquivo duplicado", "arquivo de entrada inexistente",
        "caminho inválido", "referência local inexistente", "conteúdo potencialmente inseguro",
        "modelo não informou", "existe um arquivo sem caminho",
    )
    if any(t in texto for t in transitorios):
        return "transitorio"
    if "404" in texto or "not_found" in texto:
        return "modelo"
    return "outro"


# ---------------------------------------------------------------------------
# Execução de uma etapa, com novas tentativas e modelos de reserva
# ---------------------------------------------------------------------------
def _rodar_etapa(nome: str, valores: dict[str, str], modelo: str | None, verbose: bool):
    cfg_agentes = _carregar_yaml("agents.yaml")
    cfg = _carregar_yaml("tasks.yaml")[nome]
    modelos_saida = {
        "implementar": ProgramaGerado,
        "revisar": ProgramaGerado,
        "gerar_natural": ProgramaGerado,
        "avaliar": ProgramaGerado,
        "comparar": RelatorioGerado,
    }
    modelo_saida = modelos_saida.get(nome)

    ultimo_erro: Exception | None = None
    for nome_modelo in modelos_candidatos(modelo):
        for tentativa in range(len(ESPERAS_SEGUNDOS) + 1):
            print(f"\n>> Etapa '{nome}' | modelo {nome_modelo} | tentativa {tentativa + 1}")
            try:
                agente = Agent(
                    **cfg_agentes[cfg["agent"]],
                    llm=criar_llm(nome_modelo),
                    verbose=verbose,
                    allow_delegation=False,
                )
                tarefa = Task(
                    description=_preencher(cfg["description"], valores),
                    expected_output=cfg["expected_output"],
                    agent=agente,
                    output_pydantic=modelo_saida,
                )
                crew = Crew(
                    agents=[agente],
                    tasks=[tarefa],
                    process=Process.sequential,
                    verbose=verbose,
                )
                resultado = crew.kickoff()
                if modelo_saida is not None and resultado.pydantic is None:
                    raise ValueError("O modelo não retornou a saída estruturada esperada")
                if isinstance(resultado.pydantic, ProgramaGerado):
                    _validar_programa(resultado.pydantic)
                elif isinstance(resultado.pydantic, RelatorioGerado) and not resultado.pydantic.relatorio.strip():
                    raise ValueError("O modelo retornou um relatório comparativo vazio")
                if modelo_saida is None and not (resultado.raw or "").strip():
                    raise ValueError("None or empty: resposta vazia")
                return resultado.pydantic if modelo_saida is not None else resultado.raw
            except Exception as erro:  # noqa: BLE001 - classificado abaixo
                ultimo_erro = erro
                tipo = _tipo_erro(erro)
                if tipo == "outro":
                    raise
                if tipo == "modelo":
                    print(f">> {nome_modelo} não está disponível para sua chave; tentando o próximo.")
                    break
                if tentativa < len(ESPERAS_SEGUNDOS):
                    espera = ESPERAS_SEGUNDOS[tentativa]
                    print(f">> Falha temporária ({str(erro)[:80]}...). Nova tentativa em {espera}s.")
                    time.sleep(espera)
                else:
                    print(f">> {nome_modelo} continua falhando; tentando o próximo modelo.")
    raise RuntimeError(
        f"A etapa '{nome}' falhou em todos os modelos. Tente mais tarde ou ajuste "
        "SDD_MODEL / SDD_MODELOS_RESERVA no .env (veja: python main.py --modelos)."
    ) from ultimo_erro


# ---------------------------------------------------------------------------
# Gravação
# ---------------------------------------------------------------------------
def _caminho_seguro(base: Path, relativo: str) -> Path:
    """Impede caminhos absolutos, vazios, em fora da pasta de saída."""
    texto = relativo.strip().replace("\\", "/")
    if not texto or texto.startswith("/"):
        raise ValueError(f"Caminho inválido gerado pelo modelo: {relativo}")
    destino = (base.resolve() / texto).resolve()
    if base.resolve() not in destino.parents and destino != base.resolve():
        raise ValueError(f"Caminho inválido gerado pelo modelo: {relativo}")
    if destino.is_dir():
        raise ValueError(f"Caminho esperado como arquivo: {relativo}")
    return destino


def _escrever_texto_atomico(destino: Path, conteudo: str) -> None:
    """Escreve o conteúdo via arquivo temporário e substituição final."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_name(destino.name + ".tmp")
    temporario.write_text(conteudo, encoding="utf-8")
    temporario.replace(destino)


def _validar_programa(programa: ProgramaGerado) -> None:
    if not programa.arquivos:
        raise ValueError("O modelo não retornou nenhum arquivo")
    caminhos: set[str] = set()
    entrada = (programa.entrada or "index.html").strip().replace("\\", "/")
    if not entrada:
        raise ValueError("O modelo não informou o arquivo de entrada")
    for arquivo in programa.arquivos:
        caminho = arquivo.caminho.strip().replace("\\", "/")
        if not caminho:
            raise ValueError("Existe um arquivo sem caminho")
        if not arquivo.conteudo.strip():
            raise ValueError(f"Arquivo vazio gerado pelo modelo: {caminho}")
        if caminho in caminhos:
            raise ValueError(f"Arquivo duplicado no resultado: {caminho}")
        caminhos.add(caminho)
    if entrada not in caminhos:
        raise ValueError(f"Arquivo de entrada inexistente no resultado: {entrada}")

    arquivos_por_caminho = {
        arquivo.caminho.strip().replace("\\", "/"): arquivo.conteudo
        for arquivo in programa.arquivos
    }

    # Valida referências locais antes da gravação. URLs externas e fragmentos
    # internos não são arquivos locais.
    for caminho, conteudo in arquivos_por_caminho.items():
        if not caminho.lower().endswith(".html"):
            continue
        for atributo in re.findall(
            r"""(?:src|href)\s*=\s*["']([^"']+)["']""",
            conteudo,
            flags=re.IGNORECASE,
        ):
            referencia = atributo.strip().split("#", 1)[0].split("?", 1)[0]
            if not referencia or re.match(r"^(?:[a-z][a-z0-9+.-]*:|//)", referencia, re.IGNORECASE):
                continue
            if referencia.startswith("/"):
                continue
            diretorio = str(PurePosixPath(caminho).parent)
            alvo = posixpath.normpath(posixpath.join(diretorio, referencia))
            if alvo == ".":
                alvo = ""
            if alvo not in caminhos:
                raise ValueError(
                    f"Referência local inexistente no HTML {caminho}: {referencia}"
                )

    # Os agentes são instruídos a não inserir HTML no código a partir de dados
    # dinâmicos. Essa proteção evita que um modelo retorne uma vulnerabilidade
    # de XSS ainda que a revisão tenha sido superficial.
    for caminho, conteudo in arquivos_por_caminho.items():
        if not caminho.lower().endswith(".js"):
            continue
        if re.search(r"\.(?:innerHTML|outerHTML)\s*=", conteudo):
            raise ValueError(
                f"Conteúdo potencialmente inseguro gerado no arquivo {caminho}: uso de innerHTML/outerHTML"
            )
        if re.search(r"\bdocument\.(?:write|writeln)\s*\(", conteudo):
            raise ValueError(
                f"Conteúdo potencialmente inseguro gerado no arquivo {caminho}: uso de document.write"
            )


def gravar(programa: ProgramaGerado, pasta: Path, relatorio_sdd: bool = True) -> Path:
    _validar_programa(programa)
    pasta.mkdir(parents=True, exist_ok=True)
    for arq in programa.arquivos:
        destino = _caminho_seguro(pasta, arq.caminho)
        _escrever_texto_atomico(destino, arq.conteudo)
    if relatorio_sdd and programa.relatorio:
        _escrever_texto_atomico(
            pasta / "RELATORIO_RASTREABILIDADE.md",
            programa.relatorio,
        )
    return _caminho_seguro(pasta, programa.entrada or "index.html")


def _como_texto(programa: ProgramaGerado) -> str:
    return "\n\n".join(f"--- ARQUIVO: {a.caminho} ---\n{a.conteudo}" for a in programa.arquivos)


def _codigo_com_linhas(programa: ProgramaGerado) -> str:
    """Formata arquivos com linhas numeradas para evidências da revisão natural."""
    arquivos = []
    for arquivo in programa.arquivos:
        linhas = "\n".join(
            f"{numero:4} | {linha}"
            for numero, linha in enumerate(arquivo.conteudo.splitlines(), start=1)
        )
        arquivos.append(f"--- ARQUIVO: {arquivo.caminho} ---\n{linhas}")
    return "\n\n".join(arquivos)


def _ler_pedido(prompt: str | Path) -> str:
    """Aceita o texto do pedido ou o caminho de um arquivo .md/.txt."""
    caminho = prompt if isinstance(prompt, Path) else Path(prompt)
    if isinstance(prompt, Path) or (caminho.suffix.lower() in {".md", ".txt"} and caminho.is_file()):
        if not caminho.is_file():
            raise FileNotFoundError(f"Pedido em Markdown não encontrado: {caminho}")
        try:
            pedido = caminho.read_text(encoding="utf-8")
        except UnicodeDecodeError as erro:
            raise ValueError(f"O arquivo {caminho} não está em codificação UTF-8.") from erro
    else:
        pedido = str(prompt)
    if not pedido.strip():
        raise ValueError("O pedido em linguagem natural está vazio")
    if len(pedido) > MAX_ESPECIFICACAO_CHARS:
        raise ValueError(f"O pedido excede o limite de {MAX_ESPECIFICACAO_CHARS:,} caracteres")
    return pedido


def _revisar(programa: ProgramaGerado, pedido: str, modelo: str | None, verbose: bool) -> ProgramaGerado:
    """Revisão opcional, idêntica para SDD e natural. Se falhar, mantém o original."""
    try:
        revisado = _rodar_etapa(
            "revisar", {"SPEC": pedido, "CODIGO": _como_texto(programa)}, modelo, verbose
        )
        if isinstance(revisado, ProgramaGerado):
            return revisado
    except (RuntimeError, ValueError) as erro:
        print(f"\n>> AVISO: revisão não concluída ({erro}). Mantida a versão do desenvolvedor.")
    return programa


def gerar_aplicacao_por_prompt(
    prompt: str | Path,
    pasta_saida: Path,
    verbose: bool = True,
    modelo: str | None = None,
    revisar: bool = False,
) -> Path:
    """Versão em linguagem natural: pedido -> desenvolvedor (sem SDD)."""
    pedido = _ler_pedido(prompt)
    programa = _rodar_etapa("gerar_natural", {"PROMPT": pedido}, modelo, verbose)
    if not isinstance(programa, ProgramaGerado):
        raise RuntimeError("O agente não retornou os arquivos estruturados.")
    if revisar:
        programa = _revisar(programa, pedido, modelo, verbose)
    entrada = gravar(programa, pasta_saida, relatorio_sdd=False)
    _escrever_texto_atomico(
        pasta_saida / "PEDIDO_NATURAL.md", "# Pedido em linguagem natural\n\n" + pedido
    )
    if programa.relatorio:
        _escrever_texto_atomico(
            pasta_saida / "LIMITACOES.md",
            "# Relatório do desenvolvedor (linguagem natural)\n\n" + programa.relatorio,
        )
    return entrada


def _ultima_pasta_gerada(tipo: str = "auto") -> Path:
    raizes = {
        "sdd": Path("output"),
        "natural": Path("natural_language"),
        "auto": None,
    }
    candidatos: list[Path] = []
    if tipo == "auto":
        for raiz in (Path("output"), Path("natural_language")):
            if raiz.is_dir():
                candidatos.extend(p for p in raiz.iterdir() if p.is_dir())
    else:
        raiz = raizes[tipo]
        if raiz.is_dir():
            candidatos.extend(p for p in raiz.iterdir() if p.is_dir())
    if not candidatos:
        raise RuntimeError("Nenhuma geração encontrada em output/ ou natural_language/.")
    return max(candidatos, key=lambda p: p.stat().st_mtime)


def _tipo_geracao(base: Path) -> str:
    if base.joinpath("PLANO_TECNICO.md").is_file() or base.joinpath("RELATORIO_RASTREABILIDADE.md").is_file():
        return "sdd"
    if base.joinpath("LIMITACOES.md").is_file() or "natural_language" in base.parts:
        return "natural"
    return "natural"


def _ler_documentos(base: Path) -> str:
    caminhos = [base] if base.is_file() else sorted(base.rglob("*"))
    extensoes = {".html", ".css", ".js", ".md", ".json", ".txt"}
    partes: list[str] = []
    arquivos_ignorados: list[str] = []
    limite_total = 250_000
    tamanho_total = 0
    for caminho in caminhos:
        if not caminho.is_file() or caminho.suffix.lower() not in extensoes:
            continue
        if any(parte in {".git", ".venv", "node_modules"} for parte in caminho.parts):
            continue
        try:
            conteudo = caminho.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            arquivos_ignorados.append(f"{caminho}: codificação diferente de UTF-8")
            continue
        except OSError as erro:
            arquivos_ignorados.append(f"{caminho}: {erro}")
            continue
        relativo = caminho.name if base.is_file() else caminho.relative_to(base).as_posix()
        espaco = limite_total - tamanho_total
        if espaco <= 0:
            arquivos_ignorados.append(f"{relativo}: limite total de leitura excedido")
            break
        limite_arquivo = min(50_000, espaco)
        if len(conteudo) > limite_arquivo:
            marcador = "\n[... conteúdo truncado ...]"
            if limite_arquivo > len(marcador):
                conteudo = conteudo[: limite_arquivo - len(marcador)] + marcador
            else:
                conteudo = conteudo[:limite_arquivo]
            arquivos_ignorados.append(f"{relativo}: conteúdo truncado pelo limite de leitura")
        tamanho_total += len(conteudo)
        partes.append(f"--- ARQUIVO: {relativo} ---\n{conteudo}")
    if not partes:
        raise RuntimeError(f"Nenhum arquivo de código/documentação encontrado em {base}.")
    if arquivos_ignorados:
        partes.append(
            "--- AVISO: arquivos total ou parcialmente ignorados ---\n"
            + "\n".join(f"- {item}" for item in arquivos_ignorados)
        )
    return "\n\n".join(partes)


EXTENSOES_CODIGO = {".html", ".htm", ".css", ".js"}


def _arquivos_codigo(base: Path) -> list[Path]:
    """Somente o código do programa: sem planos, relatórios ou o pedido original."""
    if base.is_file():
        return [base]
    return sorted(
        p for p in base.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSOES_CODIGO
        and not any(parte in {".git", ".venv", "node_modules"} for parte in p.parts)
    )


def _codigo_para_avaliacao(base: Path) -> str:
    """Código numerado por linha e sem documentos que revelem como foi gerado."""
    programa = ProgramaGerado(arquivos=[
        ArquivoGerado(
            caminho=p.name if base.is_file() else p.relative_to(base).as_posix(),
            conteudo=p.read_text(encoding="utf-8", errors="replace"),
        )
        for p in _arquivos_codigo(base)
    ])
    if not programa.arquivos:
        raise RuntimeError(f"Nenhum arquivo HTML/CSS/JS encontrado em {base}.")
    return _codigo_com_linhas(programa)


def metricas_objetivas(base: Path) -> dict:
    """Métricas que não dependem de LLM: testes no navegador e tamanho do código."""
    arquivos = _arquivos_codigo(base)
    linhas = {".html": 0, ".css": 0, ".js": 0}
    for p in arquivos:
        ext = ".html" if p.suffix.lower() == ".htm" else p.suffix.lower()
        linhas[ext] += sum(1 for linha in p.read_text(encoding="utf-8", errors="replace").splitlines() if linha.strip())
    pasta = base if base.is_dir() else base.parent
    entrada = "index.html" if (pasta / "index.html").is_file() else (arquivos[0].name if arquivos else "index.html")
    problemas, metodo = validar(pasta, entrada)
    return {
        "arquivos": len(arquivos),
        "linhas_html": linhas[".html"],
        "linhas_css": linhas[".css"],
        "linhas_js": linhas[".js"],
        "linhas_total": sum(linhas.values()),
        "problemas": problemas,
        "metodo_validacao": metodo,
    }


def _tabela_metricas(rotulos: dict[str, dict]) -> str:
    nomes = list(rotulos)
    linhas = [
        "| Métrica | " + " | ".join(nomes) + " |",
        "|---|" + "---|" * len(nomes),
    ]
    for chave, titulo in (
        ("arquivos", "Arquivos HTML/CSS/JS"),
        ("linhas_html", "Linhas HTML (não vazias)"),
        ("linhas_css", "Linhas CSS (não vazias)"),
        ("linhas_js", "Linhas JS (não vazias)"),
        ("linhas_total", "Linhas de código no total"),
    ):
        linhas.append(f"| {titulo} | " + " | ".join(str(rotulos[n][chave]) for n in nomes) + " |")
    linhas.append(
        "| Problemas no teste automático | "
        + " | ".join(str(len(rotulos[n]["problemas"])) for n in nomes) + " |"
    )
    texto = "\n".join(linhas) + "\n"
    for nome in nomes:
        m = rotulos[nome]
        texto += f"\n**{nome}** — validação: {m['metodo_validacao']}\n"
        texto += "".join(f"\n- {p.splitlines()[0]}" for p in m["problemas"]) or "\n- nenhum problema encontrado"
        texto += "\n"
    return texto


def comparar_codigo(
    sdd: Path,
    natural: Path,
    verbose: bool = True,
    modelo: str | None = None,
    referencia: Path | None = None,
    destino: Path | None = None,
    semente: int | None = None,
) -> Path:
    """Compara às cegas a versão SDD e a versão natural contra a mesma referência.

    A referência (gabarito) é a especificação SDD completa. Se não for informada,
    usa o ESPECIFICACAO.md gravado junto da geração SDD.
    """
    for rotulo, caminho in (("SDD", sdd), ("natural", natural)):
        if not caminho.exists():
            raise RuntimeError(f"Geração {rotulo} não encontrada: {caminho}")
    if referencia is None:
        referencia = (sdd if sdd.is_dir() else sdd.parent) / "ESPECIFICACAO.md"
    if not referencia.is_file():
        raise RuntimeError(
            f"Especificação de referência não encontrada: {referencia}. "
            "Informe-a com --referencia specs/<spec>.md"
        )

    metricas = {"SDD": metricas_objetivas(sdd), "Natural": metricas_objetivas(natural)}

    # Cegamento: o avaliador vê apenas "A" e "B", em ordem sorteada, e só o código.
    sorteio = random.Random(semente)
    ordem = ["SDD", "Natural"]
    sorteio.shuffle(ordem)
    mapa = dict(zip(("A", "B"), ordem))
    caminhos = {"SDD": sdd, "Natural": natural}

    resultado = _rodar_etapa(
        "comparar",
        {
            "REFERENCIA": referencia.read_text(encoding="utf-8"),
            "METRICAS": _tabela_metricas({f"Versão {k}": metricas[v] for k, v in mapa.items()}),
            "CODIGO_A": _codigo_para_avaliacao(caminhos[mapa["A"]]),
            "CODIGO_B": _codigo_para_avaliacao(caminhos[mapa["B"]]),
        },
        modelo,
        verbose,
    )
    if not isinstance(resultado, RelatorioGerado):
        raise RuntimeError("O avaliador comparativo não retornou um relatório estruturado.")

    if destino is None:
        nome_sdd = sdd.name if sdd.is_dir() else sdd.stem
        nome_natural = natural.name if natural.is_dir() else natural.stem
        destino = Path("comparacoes") / f"{nome_sdd}_vs_{nome_natural}"
    destino.mkdir(parents=True, exist_ok=True)
    relatorio = (
        "# Comparação às cegas — SDD vs Linguagem Natural\n\n"
        f"Referência (gabarito): `{referencia}`\n\n"
        "## Métricas objetivas (sem LLM)\n\n"
        + _tabela_metricas(metricas)
        + "\n## Avaliação do LLM (às cegas)\n\n"
        + resultado.relatorio.strip()
        + "\n\n## Revelação do cegamento\n\n"
        + "\n".join(f"- **Versão {k}** = {v} (`{caminhos[v]}`)" for k, v in mapa.items())
        + "\n"
    )
    _escrever_texto_atomico(destino / "RELATORIO_COMPARATIVO.md", relatorio)
    return destino / "RELATORIO_COMPARATIVO.md"


def avaliar_codigo(
    alvo: Path | None = None,
    verbose: bool = True,
    modelo: str | None = None,
    tipo: str = "auto",
) -> Path:
    """Avalia o último SDD/natural ou o alvo informado e grava o relatório."""
    if tipo not in {"auto", "sdd", "natural"}:
        raise ValueError("tipo deve ser auto, sdd ou natural")
    base = _ultima_pasta_gerada(tipo) if alvo is None else alvo
    if not base.exists():
        raise RuntimeError(f"Caminho para avaliação não encontrado: {base}")

    tipo_detectado = tipo if tipo in {"sdd", "natural"} else _tipo_geracao(base)
    codigo = _ler_documentos(base)
    candidatos = []
    if base.is_dir():
        candidatos.extend([
            base / "ESPECIFICACAO_DERIVADA.md",
            base / "PLANO_TECNICO.md",
            base / "RELATORIO_RASTREABILIDADE.md",
            base / "LIMITACOES.md",
            base / "PEDIDO_NATURAL.md",
            base / "RASTREABILIDADE_NATURAL.md",
            base / "README.md",
        ])
    especificacao = "\n\n".join(
        f"--- {caminho.name} ---\n{caminho.read_text(encoding='utf-8')}"
        for caminho in candidatos
        if caminho.is_file()
    ) or "Não há especificação ou plano armazenado no alvo. Avaliar apenas contra os arquivos presentes."

    programa_corrigido = _rodar_etapa(
        "avaliar",
        {
            "ESPECIFICACAO": especificacao,
            "CODIGO": codigo,
            "TIPO_AVALIACAO": f"{tipo_detectado.upper()} — avalie e corrija conforme este tipo de geração.",
        },
        modelo,
        verbose,
    )
    if not isinstance(programa_corrigido, ProgramaGerado):
        raise RuntimeError("O avaliador não retornou arquivos corrigidos estruturados.")

    destino = base if base.is_dir() else base.parent
    destino.mkdir(parents=True, exist_ok=True)
    if base.is_dir():
        gravar(programa_corrigido, destino, relatorio_sdd=False)
    elif base.is_file():
        correspondentes = [
            arquivo
            for arquivo in programa_corrigido.arquivos
            if PurePosixPath(arquivo.caminho.replace("\\", "/")).name == base.name
        ]
        if len(correspondentes) == 1:
            arquivo_corrigido = correspondentes[0]
        elif len(programa_corrigido.arquivos) == 1:
            arquivo_corrigido = programa_corrigido.arquivos[0]
        else:
            raise RuntimeError(
                f"A avaliação retornou vários arquivos sem identificar qual corresponde a {base.name}."
            )
        _escrever_texto_atomico(base, arquivo_corrigido.conteudo)

    relatorio = programa_corrigido.relatorio or "A avaliação não produziu achados textuais."
    arquivo = destino / "RELATORIO_AVALIACAO.md"
    cabecalho = f"# Relatório de avaliação — {tipo_detectado.upper()}\n\n"
    if relatorio.lstrip().startswith("#"):
        relatorio = cabecalho + relatorio.lstrip()
    else:
        relatorio = cabecalho + relatorio
    arquivo.write_text(relatorio, encoding="utf-8")
    if tipo_detectado == "natural":
        matriz = (
            "# Rastreabilidade da linguagem natural\n\n"
            "| Ponto solicitado | Implementação encontrada | Arquivo / linha | Status | Evidência |\n"
            "|---|---|---|---|---|\n"
            "| Derivado do pedido | Ver matriz detalhada no relatório de avaliação | Arquivos HTML/CSS/JS | Ver abaixo | Evidências verificadas no código |\n\n"
            "## Matriz detalhada da avaliação\n\n"
            + relatorio
        )
        (destino / "RASTREABILIDADE_NATURAL.md").write_text(matriz, encoding="utf-8")
    return arquivo


# ---------------------------------------------------------------------------
def gerar_aplicacao(
    arquivo_spec: Path,
    pasta_saida: Path,
    verbose: bool = True,
    modelo: str | None = None,
    revisar: bool = False,
) -> Path:
    """Versão SDD: especificação -> analista (plano) -> desenvolvedor."""
    if not arquivo_spec.is_file():
        raise ValueError(f"Especificação não encontrada: {arquivo_spec}")
    spec = arquivo_spec.read_text(encoding="utf-8")
    if not spec.strip():
        raise ValueError("A especificação está vazia")
    if len(spec) > MAX_ESPECIFICACAO_CHARS:
        raise ValueError(
            f"Especificação excede o limite de {MAX_ESPECIFICACAO_CHARS:,} caracteres"
        )
    pasta_saida.mkdir(parents=True, exist_ok=True)
    _escrever_texto_atomico(pasta_saida / "ESPECIFICACAO.md", spec)
    valores = {"SPEC": spec, "ARQUIVO": arquivo_spec.name}

    # 1) Análise -> plano técnico (salvo já, para não se perder)
    plano = _rodar_etapa("analisar", valores, modelo, verbose)
    _escrever_texto_atomico(pasta_saida / "PLANO_TECNICO.md", plano)
    valores["PLANO"] = plano

    # 2) Implementação completa em uma única passagem.
    programa = _rodar_etapa("implementar", valores, modelo, verbose)
    if not isinstance(programa, ProgramaGerado):
        raise RuntimeError("O desenvolvedor não retornou arquivos estruturados")

    # 3) Revisão opcional (a mesma usada na versão natural).
    if revisar:
        programa = _revisar(programa, spec, modelo, verbose)
    entrada = gravar(programa, pasta_saida)
    print(f"\n>> Aplicação SDD salva em {pasta_saida}")
    return entrada


def executar_experimento(
    arquivo_spec: Path,
    pedido_natural: Path,
    pasta: Path | None = None,
    verbose: bool = True,
    modelo: str | None = None,
    revisar: bool = False,
) -> Path:
    """Gera as duas versões nas mesmas condições e compara às cegas."""
    pasta = pasta or Path("experimentos") / arquivo_spec.stem
    print(f"\n=== Experimento: {arquivo_spec} (SDD) x {pedido_natural} (natural) ===")
    gerar_aplicacao(arquivo_spec, pasta / "sdd", verbose, modelo, revisar)
    gerar_aplicacao_por_prompt(pedido_natural, pasta / "natural", verbose, modelo, revisar)
    return comparar_codigo(
        pasta / "sdd", pasta / "natural", verbose, modelo,
        referencia=arquivo_spec, destino=pasta,
    )
