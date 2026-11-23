import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml
from crewai import LLM, Agent, Crew, Task
from pydantic import BaseModel

PASTA_CONFIG = Path(__file__).parent / "config"
MODELO_PADRAO = "gemini/gemini-3.5-flash"
TENTATIVAS = 3
EXTENSOES_CODIGO = (".html", ".css", ".js")

Status = Literal["atendido", "parcial", "não atendido"]
PONTOS = {"atendido": 1.0, "parcial": 0.5, "não atendido": 0.0}


class Arquivo(BaseModel):
    caminho: str
    conteudo: str


class Programa(BaseModel):
    arquivos: list[Arquivo]


class Requisito(BaseModel):
    id: str
    descricao: str
    versao_a: Status
    evidencia_a: str
    versao_b: Status
    evidencia_b: str


class Comparacao(BaseModel):
    requisitos: list[Requisito]
    conclusao: str


@dataclass
class Execucao:
    """Resultado de um agente: a saída e as métricas medidas."""
    saida: BaseModel
    segundos: float
    tokens_entrada: int
    tokens_saida: int
    tokens_total: int
    tentativas: int


def carregar_yaml(nome):
    with open(PASTA_CONFIG / nome, encoding="utf-8") as arquivo:
        return yaml.safe_load(arquivo)


def criar_llm(modelo):
    max_tokens = int(os.getenv("SDD_MAX_TOKENS", "32768"))
    return LLM(model=modelo, temperature=0.2, max_tokens=max_tokens)


def executar(nome_tarefa, valores, formato, modelo):
    """Roda uma tarefa com o seu agente e mede o tempo e os tokens gastos.

    Se a API falhar (ex.: servidor sobrecarregado), tenta de novo. O tempo e os
    tokens registrados são os da tentativa que deu certo.
    """
    config_tarefa = carregar_yaml("tasks.yaml")[nome_tarefa]
    config_agente = carregar_yaml("agents.yaml")[config_tarefa["agent"]]

    descricao = config_tarefa["description"]
    for chave, valor in valores.items():
        descricao = descricao.replace(f"[[{chave}]]", valor)

    for tentativa in range(1, TENTATIVAS + 1):
        print(f"> {nome_tarefa} (tentativa {tentativa})")
        agente = Agent(**config_agente, llm=criar_llm(modelo), allow_delegation=False, verbose=False)
        tarefa = Task(
            description=descricao,
            expected_output=config_tarefa["expected_output"],
            agent=agente,
            output_pydantic=formato,
        )
        crew = Crew(agents=[agente], tasks=[tarefa], verbose=False)
        try:
            inicio = time.perf_counter()
            resultado = crew.kickoff()
            segundos = time.perf_counter() - inicio
            if resultado.pydantic is None:
                raise ValueError("o modelo não devolveu a saída no formato esperado")
        except Exception as erro:
            if tentativa == TENTATIVAS:
                raise RuntimeError(f"{nome_tarefa} falhou: {erro}") from erro
            print(f"  erro: {str(erro)[:120]}. Tentando de novo em 10 s.")
            time.sleep(10)
            continue

        uso = resultado.token_usage
        return Execucao(
            saida=resultado.pydantic,
            segundos=round(segundos, 1),
            tokens_entrada=uso.prompt_tokens,
            tokens_saida=uso.completion_tokens,
            tokens_total=uso.total_tokens,
            tentativas=tentativa,
        )


def salvar_programa(programa, pasta):
    pasta.mkdir(parents=True, exist_ok=True)
    raiz = pasta.resolve()
    for arquivo in programa.arquivos:
        destino = (raiz / arquivo.caminho.strip().lstrip("/")).resolve()
        if raiz not in destino.parents:
            raise ValueError(f"caminho inválido gerado pelo modelo: {arquivo.caminho}")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(arquivo.conteudo, encoding="utf-8")


def ler_codigo(pasta):
    """Junta o código da pasta com as linhas numeradas, para o comparador citar."""
    partes = []
    for caminho in sorted(pasta.rglob("*")):
        if caminho.suffix.lower() not in EXTENSOES_CODIGO:
            continue
        linhas = caminho.read_text(encoding="utf-8").splitlines()
        numeradas = "\n".join(f"{n:4} | {linha}" for n, linha in enumerate(linhas, 1))
        partes.append(f"--- {caminho.relative_to(pasta).as_posix()} ---\n{numeradas}")
    return "\n\n".join(partes)


def cobertura(requisitos, campo):
    pontos = sum(PONTOS[getattr(r, campo)] for r in requisitos)
    return round(100 * pontos / len(requisitos), 1) if requisitos else 0.0


def rodar_experimento(arquivo_md, arquivo_txt, pasta_saida, modelo=None, seed=None):
    modelo = modelo or os.getenv("SDD_MODEL", MODELO_PADRAO)
    especificacao = arquivo_md.read_text(encoding="utf-8")
    pedido = arquivo_txt.read_text(encoding="utf-8")

    sdd = executar("desenvolver_sdd", {"ENTRADA": especificacao}, Programa, modelo)
    salvar_programa(sdd.saida, pasta_saida / "sdd")

    natural = executar("desenvolver_natural", {"ENTRADA": pedido}, Programa, modelo)
    salvar_programa(natural.saida, pasta_saida / "natural")

    # O comparador não sabe qual versão é qual: a ordem A/B é sorteada.
    versoes = ["sdd", "natural"]
    random.Random(seed).shuffle(versoes)
    a, b = versoes
    comparacao = executar(
        "comparar",
        {
            "ESPECIFICACAO": especificacao,
            "VERSAO_A": ler_codigo(pasta_saida / a),
            "VERSAO_B": ler_codigo(pasta_saida / b),
        },
        Comparacao,
        modelo,
    )

    relatorio = montar_relatorio(arquivo_md, arquivo_txt, modelo, sdd, natural, comparacao, a)
    (pasta_saida / "relatorio.md").write_text(relatorio, encoding="utf-8")
    return pasta_saida / "relatorio.md"


def montar_relatorio(arquivo_md, arquivo_txt, modelo, sdd, natural, comparacao, versao_a):
    requisitos = comparacao.saida.requisitos
    # Traduz A/B de volta para SDD/natural.
    campo_sdd, campo_natural = ("versao_a", "versao_b") if versao_a == "sdd" else ("versao_b", "versao_a")
    evid_sdd, evid_natural = campo_sdd.replace("versao", "evidencia"), campo_natural.replace("versao", "evidencia")

    def contar(campo, status):
        return sum(1 for r in requisitos if getattr(r, campo) == status)

    linhas = [
        "# Comparação SDD x linguagem natural",
        "",
        f"- Especificação (agente SDD): `{arquivo_md}`",
        f"- Pedido (agente natural): `{arquivo_txt}`",
        f"- Modelo: `{modelo}`",
        "",
        "## Métricas",
        "",
        "| Métrica | SDD | Linguagem natural |",
        "|---|---|---|",
        f"| Tempo de geração (s) | {sdd.segundos} | {natural.segundos} |",
        f"| Tokens de entrada | {sdd.tokens_entrada} | {natural.tokens_entrada} |",
        f"| Tokens de saída | {sdd.tokens_saida} | {natural.tokens_saida} |",
        f"| Tokens totais | {sdd.tokens_total} | {natural.tokens_total} |",
        f"| Requisitos atendidos | {contar(campo_sdd, 'atendido')} | {contar(campo_natural, 'atendido')} |",
        f"| Requisitos parciais | {contar(campo_sdd, 'parcial')} | {contar(campo_natural, 'parcial')} |",
        f"| Requisitos não atendidos | {contar(campo_sdd, 'não atendido')} | {contar(campo_natural, 'não atendido')} |",
        f"| Cobertura dos requisitos | {cobertura(requisitos, campo_sdd)}% | {cobertura(requisitos, campo_natural)}% |",
        "",
        f"Total de requisitos avaliados: {len(requisitos)}. Cobertura: atendido = 1, parcial = 0,5.",
        "",
        "## Requisitos",
        "",
        "| Requisito | Descrição | SDD | Evidência SDD | Natural | Evidência natural |",
        "|---|---|---|---|---|---|",
    ]
    for r in requisitos:
        celulas = [
            r.id, r.descricao,
            getattr(r, campo_sdd), getattr(r, evid_sdd),
            getattr(r, campo_natural), getattr(r, evid_natural),
        ]
        linhas.append("| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in celulas) + " |")

    nome_a = "SDD" if versao_a == "sdd" else "linguagem natural"
    nome_b = "linguagem natural" if versao_a == "sdd" else "SDD"
    linhas += [
        "",
        "## Conclusão do comparador",
        "",
        f"O comparador avaliou sem saber a origem: Versão A = {nome_a}, Versão B = {nome_b}.",
        "",
        comparacao.saida.conclusao.strip(),
        "",
        f"Comparador: {comparacao.segundos} s, {comparacao.tokens_total} tokens.",
        "",
    ]
    return "\n".join(linhas)
