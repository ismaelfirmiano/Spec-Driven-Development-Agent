"""Pipeline de Spec-Driven Development com CrewAI + Gemini.

As três etapas (analisar -> implementar -> revisar) rodam uma de cada vez.
Assim, se o modelo falhar no meio, só a etapa que falhou é repetida, e o
resultado de cada etapa já fica salvo em disco.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path

import yaml
from crewai import LLM, Agent, Crew, Process, Task
from pydantic import BaseModel, Field

CONFIG_DIR = Path(__file__).parent / "config"
MODELO_PADRAO = "gemini/gemini-3.8-flash"
RESERVA_PADRAO = "gemini/gemini-flash-latest,gemini/gemini-flash-lite-latest"
ESPERAS_SEGUNDOS = (15, 45)  # pausas entre tentativas no mesmo modelo
MAX_TOKENS_PADRAO = 32768    # espaço para o código completo na resposta


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


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
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
    max_tokens = int(os.getenv("SDD_MAX_TOKENS", MAX_TOKENS_PADRAO))
    return LLM(model=modelo, temperature=0.2, max_tokens=max_tokens)


def _tipo_erro(erro: Exception) -> str:
    """'transitorio' (vale repetir), 'modelo' (trocar de modelo) ou 'outro'."""
    texto = str(erro)
    transitorios = (
        "503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "high demand", "overloaded",
        "None or empty", "500", "INTERNAL", "timed out", "Timeout",
    )
    if any(t in texto for t in transitorios):
        return "transitorio"
    if "404" in texto or "NOT_FOUND" in texto:
        return "modelo"
    return "outro"


# ---------------------------------------------------------------------------
# Execução de uma etapa, com novas tentativas e modelos de reserva
# ---------------------------------------------------------------------------
def _rodar_etapa(nome: str, valores: dict[str, str], modelo: str | None, verbose: bool):
    cfg_agentes = _carregar_yaml("agents.yaml")
    cfg = _carregar_yaml("tasks.yaml")[nome]
    estruturada = nome in ("implementar", "revisar")

    ultimo_erro: Exception | None = None
    for nome_modelo in modelos_candidatos(modelo):
        for tentativa in range(len(ESPERAS_SEGUNDOS) + 1):
            print(f"\n>> Etapa '{nome}' | modelo {nome_modelo} | tentativa {tentativa + 1}")
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
                output_pydantic=ProgramaGerado if estruturada else None,
            )
            crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential, verbose=verbose)
            try:
                resultado = crew.kickoff()
                if estruturada and resultado.pydantic is None:
                    raise ValueError("None or empty: saída estruturada ausente")
                if not estruturada and not (resultado.raw or "").strip():
                    raise ValueError("None or empty: resposta vazia")
                return resultado.pydantic if estruturada else resultado.raw
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
    """Impede que o modelo escreva fora da pasta de saída."""
    destino = (base / relativo.lstrip("/\\")).resolve()
    if base.resolve() not in destino.parents and destino != base.resolve():
        raise ValueError(f"Caminho inválido gerado pelo modelo: {relativo}")
    return destino


def gravar(programa: ProgramaGerado, pasta: Path, relatorio_sdd: bool = True) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    for arq in programa.arquivos:
        destino = _caminho_seguro(pasta, arq.caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(arq.conteudo, encoding="utf-8")
    if relatorio_sdd and programa.relatorio:
        (pasta / "RELATORIO_RASTREABILIDADE.md").write_text(programa.relatorio, encoding="utf-8")
    return _caminho_seguro(pasta, programa.entrada or "index.html")


def _como_texto(programa: ProgramaGerado) -> str:
    return "\n\n".join(f"--- ARQUIVO: {a.caminho} ---\n{a.conteudo}" for a in programa.arquivos)


def gerar_aplicacao_por_prompt(
    prompt: str, pasta_saida: Path, verbose: bool = True, modelo: str | None = None
) -> Path:
    """Gera um protótipo direto a partir de linguagem natural, fora do pipeline SDD."""
    programa = _rodar_etapa("gerar_natural", {"PROMPT": prompt}, modelo, verbose)
    if not isinstance(programa, ProgramaGerado):
        raise RuntimeError("O agente não retornou os arquivos estruturados do protótipo.")
    entrada = gravar(programa, pasta_saida, relatorio_sdd=False)
    if programa.relatorio:
        (pasta_saida / "LIMITACOES.md").write_text(
            "# Limitações e decisões do modo linguagem natural\n\n" + programa.relatorio,
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
    for caminho in caminhos:
        if not caminho.is_file() or caminho.suffix.lower() not in extensoes:
            continue
        if any(parte in {".git", ".venv", "node_modules"} for parte in caminho.parts):
            continue
        try:
            conteudo = caminho.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        relativo = caminho.name if base.is_file() else caminho.relative_to(base).as_posix()
        if len(conteudo) > 100_000:
            conteudo = conteudo[:100_000] + "\n[... conteúdo truncado ...]"
        partes.append(f"--- ARQUIVO: {relativo} ---\n{conteudo}")
    if not partes:
        raise RuntimeError(f"Nenhum arquivo de código/documentação encontrado em {base}.")
    return "\n\n".join(partes)


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
            base / "README.md",
        ])
    especificacao = "\n\n".join(
        f"--- {caminho.name} ---\n{caminho.read_text(encoding='utf-8')}"
        for caminho in candidatos
        if caminho.is_file()
    ) or "Não há especificação ou plano armazenado no alvo. Avaliar apenas contra os arquivos presentes."

    relatorio = _rodar_etapa(
        "avaliar",
        {
            "ESPECIFICACAO": especificacao,
            "CODIGO": codigo,
            "TIPO_AVALIACAO": f"{tipo_detectado.upper()} — avalie conforme este tipo de geração.",
        },
        modelo,
        verbose,
    )
    destino = base if base.is_dir() else base.parent
    destino.mkdir(parents=True, exist_ok=True)
    arquivo = destino / "RELATORIO_AVALIACAO.md"
    cabecalho = f"# Relatório de avaliação — {tipo_detectado.upper()}\n\n"
    if relatorio.lstrip().startswith("#"):
        relatorio = cabecalho + relatorio.lstrip()
    else:
        relatorio = cabecalho + relatorio
    arquivo.write_text(relatorio, encoding="utf-8")
    return arquivo


# ---------------------------------------------------------------------------
def gerar_aplicacao(
    arquivo_spec: Path, pasta_saida: Path, verbose: bool = True, modelo: str | None = None
) -> Path:
    """Lê a especificação, executa as três etapas e devolve o caminho do index.html."""
    spec = arquivo_spec.read_text(encoding="utf-8")
    pasta_saida.mkdir(parents=True, exist_ok=True)
    valores = {"SPEC": spec, "ARQUIVO": arquivo_spec.name}

    # 1) Análise -> plano técnico (salvo já, para não se perder)
    plano = _rodar_etapa("analisar", valores, modelo, verbose)
    (pasta_saida / "PLANO_TECNICO.md").write_text(plano, encoding="utf-8")
    valores["PLANO"] = plano

    # 2) Implementação -> primeira versão do programa, já utilizável
    rascunho = _rodar_etapa("implementar", valores, modelo, verbose)
    entrada = gravar(rascunho, pasta_saida)
    print(f"\n>> Primeira versão salva em {pasta_saida}")
    valores["CODIGO"] = _como_texto(rascunho)

    # 3) Revisão -> versão final (se falhar, fica a versão do desenvolvedor)
    try:
        final = _rodar_etapa("revisar", valores, modelo, verbose)
        entrada = gravar(final, pasta_saida)
    except RuntimeError as erro:
        print(f"\n>> AVISO: revisão não concluída ({erro}). Mantida a versão do desenvolvedor.")
    return entrada
