"""Pipeline de Spec-Driven Development com CrewAI + Gemini.

As três etapas (analisar -> implementar -> revisar) rodam uma de cada vez.
Assim, se o modelo falhar no meio, só a etapa que falhou é repetida, e o
resultado de cada etapa já fica salvo em disco.
"""

from __future__ import annotations

import os
import posixpath
import re
import time
from functools import lru_cache
from pathlib import Path, PurePosixPath

import yaml
from crewai import LLM, Agent, Crew, Process, Task
from pydantic import BaseModel, Field

CONFIG_DIR = Path(__file__).parent / "config"
MODELO_PADRAO = "gemini/gemini-3.8-flash"
RESERVA_PADRAO = "gemini/gemini-3.5-flash-lite,gemini/gemini-3.1-flash-lite"
ESPERAS_SEGUNDOS = (1,)
MAX_TOKENS_PADRAO = 8192
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


def _preencher(texto: str, valores: dict[str, str]) -> str:
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


def gerar_aplicacao_por_prompt(
    prompt: str | Path, pasta_saida: Path, verbose: bool = True, modelo: str | None = None
) -> Path:
    """Gera um protótipo direto a partir de texto ou de um arquivo Markdown."""
    if isinstance(prompt, Path):
        if not prompt.is_file():
            raise FileNotFoundError(f"Pedido em Markdown não encontrado: {prompt}")
        try:
            pedido = prompt.read_text(encoding="utf-8")
        except UnicodeDecodeError as erro:
            raise ValueError(
                f"O arquivo {prompt} não está em codificação UTF-8."
            ) from erro
    else:
        candidato = Path(prompt)
        if candidato.suffix.lower() == ".md" and candidato.is_file():
            try:
                pedido = candidato.read_text(encoding="utf-8")
            except UnicodeDecodeError as erro:
                raise ValueError(
                    f"O arquivo {candidato} não está em codificação UTF-8."
                ) from erro
        else:
            pedido = prompt

    if not pedido.strip():
        raise ValueError("O pedido em linguagem natural está vazio")
    if len(pedido) > MAX_ESPECIFICACAO_CHARS:
        raise ValueError(
            f"O pedido excede o limite de {MAX_ESPECIFICACAO_CHARS:,} caracteres"
        )
    programa = _rodar_etapa(
        "gerar_natural",
        {"PROMPT": pedido},
        modelo,
        verbose,
    )
    if not isinstance(programa, ProgramaGerado):
        raise RuntimeError("O agente não retornou os arquivos estruturados do protótipo.")
    entrada = gravar(programa, pasta_saida, relatorio_sdd=False)
    (pasta_saida / "PEDIDO_NATURAL.md").write_text(
        "# Pedido em linguagem natural\n\n" + pedido,
        encoding="utf-8",
    )
    if programa.relatorio:
        (pasta_saida / "LIMITACOES.md").write_text(
            "# Limitações e decisões do modo linguagem natural\n\n" + programa.relatorio,
            encoding="utf-8",
        )
    if os.getenv("SDD_MODO_RAPIDO") == "1":
        rastreabilidade = (
            "# Rastreabilidade da linguagem natural\n\n"
            "Revisão adicional omitida pelo modo rápido; use `--avaliar` "
            "quando quiser uma auditoria técnica sob demanda.\n"
        )
    else:
        try:
            revisao = _rodar_etapa(
                "revisar_natural",
                {"PROMPT": pedido, "CODIGO": _codigo_com_linhas(programa)},
                modelo,
                verbose,
            )
            rastreabilidade = str(revisao).strip()
        except (RuntimeError, ValueError) as erro:
            rastreabilidade = (
                "# Rastreabilidade da linguagem natural\n\n"
                "A revisão natural não pôde ser concluída neste ambiente. "
                f"Motivo registrado: {erro}\n"
            )
    (pasta_saida / "RASTREABILIDADE_NATURAL.md").write_text(
        rastreabilidade
        if rastreabilidade.lower().startswith("#")
        else "# Rastreabilidade da linguagem natural\n\n" + rastreabilidade,
        encoding="utf-8",
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


def comparar_codigo(
    sdd: Path,
    natural: Path,
    verbose: bool = True,
    modelo: str | None = None,
) -> Path:
    """Compara uma geração SDD com uma geração em linguagem natural."""
    if not sdd.exists():
        raise RuntimeError(f"Geração SDD não encontrada: {sdd}")
    if not natural.exists():
        raise RuntimeError(f"Geração natural não encontrada: {natural}")

    codigo_sdd = _ler_documentos(sdd)
    codigo_natural = _ler_documentos(natural)
    resultado = _rodar_etapa(
        "comparar",
        {"CODIGO_SDD": codigo_sdd, "CODIGO_NATURAL": codigo_natural},
        modelo,
        verbose,
    )
    if not isinstance(resultado, RelatorioGerado):
        raise RuntimeError("O avaliador comparativo não retornou um relatório estruturado.")

    nome_sdd = sdd.name if sdd.is_dir() else sdd.stem
    nome_natural = natural.name if natural.is_dir() else natural.stem
    destino = Path("comparacoes") / f"{nome_sdd}_vs_{nome_natural}"
    destino.mkdir(parents=True, exist_ok=True)
    relatorio = resultado.relatorio
    relatorio = f"# Comparação — SDD vs Linguagem Natural\n\n{relatorio.lstrip('#').lstrip()}"
    (destino / "RELATORIO_COMPARATIVO.md").write_text(relatorio, encoding="utf-8")

    return destino


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
) -> Path:
    """Gera a aplicação completa em três etapas rápidas e consecutivas."""
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
    valores = {"SPEC": spec, "ARQUIVO": arquivo_spec.name}

    # 1) Análise -> plano técnico (salvo já, para não se perder)
    plano = _rodar_etapa("analisar", valores, modelo, verbose)
    (pasta_saida / "PLANO_TECNICO.md").write_text(plano, encoding="utf-8")
    valores["PLANO"] = plano

    # 2) Implementação completa em uma única passagem.
    valores["FASE"] = "entrega completa unificada das Fases 1, 2 e 3"
    rascunho = _rodar_etapa("implementar", valores, modelo, verbose)
    if not isinstance(rascunho, ProgramaGerado):
        raise RuntimeError("O desenvolvedor não retornou arquivos estruturados")
    entrada = gravar(rascunho, pasta_saida)
    print(f"\n>> Aplicação completa salva em {pasta_saida}")
    valores["CODIGO"] = _como_texto(rascunho)

    # 3) Revisão final. O modo rápido omite esta chamada e preserva o rascunho.
    if os.getenv("SDD_MODO_RAPIDO") == "1":
        return entrada

    try:
        final = _rodar_etapa("revisar", valores, modelo, verbose)
        if not isinstance(final, ProgramaGerado):
            raise RuntimeError("O revisor não retornou arquivos estruturados")
        entrada = gravar(final, pasta_saida)
    except (RuntimeError, ValueError) as erro:
        print(f"\n>> AVISO: revisão não concluída ({erro}). Mantida a versão do desenvolvedor.")
    return entrada
