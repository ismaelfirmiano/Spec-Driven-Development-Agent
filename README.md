# Spec-Driven-Development-Agent

Agente de IA que lê um arquivo de especificação e gera um programa web
(HTML/CSS/JS) pronto para abrir no navegador. Usa **CrewAI** para orquestrar
três agentes e **Gemini** (Google Gen AI) como modelo.

## Pipeline

```
spec.md ─► Analista ─► Desenvolvedor ─► [teste no navegador ─► corrigir]* ─► Revisor ─► [teste ─► corrigir]* ─► output/<spec>/
           (plano RF/RNF)  (HTML/CSS/JS)     (Playwright, até 2 rodadas)        (QA)
```

O revisor é um LLM e pode aprovar código quebrado. Por isso, cada versão passa
por uma **validação automática** (`sdd_agent/validacao.py`), que não depende do
modelo: abre o `index.html` num navegador headless, captura erros de JavaScript,
confere se os arquivos referenciados existem e envia os formulários para
detectar recarregamento da página. Se algo falha, os erros voltam para o
desenvolvedor corrigir. Sem Playwright, a validação usa `node --check`.

Saída em `output/<nome-da-spec>/`: os arquivos do programa, `PLANO_TECNICO.md`,
`RELATORIO_RASTREABILIDADE.md` (requisito → código → status) e `VALIDACAO.md`
(resultado dos testes automáticos e correções feitas).

## Instalação

> O CrewAI exige **Python ≥3.10 e <3.14**. O `setup.sh` funciona em **macOS e Linux**:
> usa um Python compatível já instalado ou instala o 3.13 (Homebrew no Mac, `uv` no Linux).

```bash
./setup.sh                 # cria .venv (Python 3.10–3.13) e instala requirements.txt
source .venv/bin/activate
# edite .env e coloque sua GEMINI_API_KEY (https://aistudio.google.com/apikey)
```

No Ubuntu/Debian, se a criação do `.venv` falhar, instale o pacote venv
(ex.: `sudo apt install python3.12-venv`).

Manual (qualquer sistema): `python3.13 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cp .env.example .env`

## Uso

```bash
python main.py specs/exemplo_tarefas.md --abrir
```

Se o modelo estiver sobrecarregado (erro 503), o agente espera e tenta de novo,
e depois passa para os modelos de `SDD_MODELOS_RESERVA` no `.env`. Para ver os
modelos que sua chave pode usar: `python main.py --modelos`. Para forçar um modelo
só nesta execução: `python main.py specs/x.md -m gemini/<nome>`.

Opções: `-o PASTA` (saída), `-m MODELO`, `-q` (sem log dos agentes), `--abrir` (abre no navegador).

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
