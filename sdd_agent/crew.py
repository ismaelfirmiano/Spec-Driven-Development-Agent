"""Monta a Crew de Spec-Driven Development e grava os arquivos gerados."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from crewai import LLM, Agent, Crew, Process, Task
from pydantic import BaseModel, Field

CONFIG_DIR = Path(__file__).parent / "config"
MODELO_PADRAO = "gemini/gemini-2.5-flash"


# ---------------------------------------------------------------------------
# Saída estruturada do revisor (garante que recebemos arquivos, não prosa)
# ---------------------------------------------------------------------------
class ArquivoGerado(BaseModel):
    caminho: str = Field(description="Caminho relativo, ex.: index.html ou css/style.css")
    conteudo: str = Field(description="Conteúdo completo do arquivo")


class ProgramaGerado(BaseModel):
    arquivos: list[ArquivoGerado]
    entrada: str = Field(default="index.html", description="Arquivo a abrir no navegador")
    relatorio: str = Field(description="Relatório de rastreabilidade em Markdown")


# ---------------------------------------------------------------------------
def _carregar_yaml(nome: str) -> dict:
    with open(CONFIG_DIR / nome, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _preencher(texto: str, valores: dict[str, str]) -> str:
    for chave, valor in valores.items():
        texto = texto.replace(f"[[{chave}]]", valor)
    return texto


def criar_llm() -> LLM:
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        raise RuntimeError("Defina GEMINI_API_KEY no arquivo .env")
    return LLM(model=os.getenv("SDD_MODEL", MODELO_PADRAO), temperature=0.2)


def montar_crew(spec: str, nome_arquivo: str, verbose: bool = True) -> Crew:
    llm = criar_llm()
    cfg_agentes = _carregar_yaml("agents.yaml")
    cfg_tarefas = _carregar_yaml("tasks.yaml")
    valores = {"SPEC": spec, "ARQUIVO": nome_arquivo}

    agentes = {
        nome: Agent(**cfg, llm=llm, verbose=verbose, allow_delegation=False)
        for nome, cfg in cfg_agentes.items()
    }

    def tarefa(nome: str, **extra) -> Task:
        cfg = cfg_tarefas[nome]
        return Task(
            description=_preencher(cfg["description"], valores),
            expected_output=cfg["expected_output"],
            agent=agentes[cfg["agent"]],
            **extra,
        )

    analisar = tarefa("analisar")
    implementar = tarefa("implementar", context=[analisar])
    revisar = tarefa("revisar", context=[analisar, implementar], output_pydantic=ProgramaGerado)

    return Crew(
        agents=list(agentes.values()),
        tasks=[analisar, implementar, revisar],
        process=Process.sequential,
        verbose=verbose,
    )


def _caminho_seguro(base: Path, relativo: str) -> Path:
    """Impede que o modelo escreva fora da pasta de saída."""
    destino = (base / relativo.lstrip("/\\")).resolve()
    if base.resolve() not in destino.parents and destino != base.resolve():
        raise ValueError(f"Caminho inválido gerado pelo modelo: {relativo}")
    return destino


def gravar(programa: ProgramaGerado, plano: str, pasta: Path) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    for arq in programa.arquivos:
        destino = _caminho_seguro(pasta, arq.caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(arq.conteudo, encoding="utf-8")
    (pasta / "PLANO_TECNICO.md").write_text(plano, encoding="utf-8")
    (pasta / "RELATORIO_RASTREABILIDADE.md").write_text(programa.relatorio, encoding="utf-8")
    return _caminho_seguro(pasta, programa.entrada or "index.html")


def gerar_aplicacao(arquivo_spec: Path, pasta_saida: Path, verbose: bool = True) -> Path:
    """Lê a especificação, executa os agentes e devolve o caminho do index.html."""
    spec = arquivo_spec.read_text(encoding="utf-8")
    crew = montar_crew(spec, arquivo_spec.name, verbose=verbose)
    resultado = crew.kickoff()

    programa = resultado.pydantic
    if programa is None:
        raise RuntimeError("O revisor não devolveu a saída estruturada esperada.")

    plano = crew.tasks[0].output.raw if crew.tasks[0].output else ""
    return gravar(programa, plano, pasta_saida)
