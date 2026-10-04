# Spec-Driven-Development-Agent

Agente de IA que lê um arquivo de especificação e gera um programa web
(HTML/CSS/JS) pronto para abrir no navegador. Usa **CrewAI** para orquestrar
três agentes e **Gemini** (Google Gen AI) como modelo.

## Pipeline

```
spec.md ──► Analista de Requisitos ──► Desenvolvedor Front-end ──► Revisor QA ──► output/<spec>/
            (plano + RF/RNF + critérios)  (HTML/CSS/JS comentado)    (corrige + rastreabilidade)
```

Saída em `output/<nome-da-spec>/`: os arquivos do programa, `PLANO_TECNICO.md`
e `RELATORIO_RASTREABILIDADE.md` (requisito → código → status).

## Instalação

> O CrewAI exige **Python ≥3.10 e <3.14**. O `setup.sh` recria o `.venv` com 3.13.

```bash
./setup.sh                 # cria .venv (Python 3.13) e instala requirements.txt
source .venv/bin/activate
# edite .env e coloque sua GEMINI_API_KEY (https://aistudio.google.com/apikey)
```

Manual: `python3.13 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cp .env.example .env`

## Uso

```bash
python main.py specs/exemplo_tarefas.md --abrir
```

Opções: `-o PASTA` (saída), `-q` (sem log dos agentes), `--abrir` (abre no navegador).

## Escrevendo uma especificação

Markdown livre; funciona melhor com requisitos identificados (`RF-01`,
`RNF-01`), critérios claros e uma seção "Fora do escopo". Veja
`specs/exemplo_tarefas.md`.

## Estrutura

```
main.py                    CLI
sdd_agent/crew.py          agentes, tarefas, saída estruturada e gravação
sdd_agent/config/*.yaml    papéis dos agentes e descrições das tarefas
specs/                     especificações de entrada
output/                    programas gerados (ignorado pelo git)
```
