# Spec-Driven-Development-Agent

Agente de IA que transforma especificações ou pedidos em linguagem natural
em programas web (HTML/CSS/JS) prontos para abrir no navegador. Usa **CrewAI**
para orquestrar agentes especializados e **Gemini** (Google Gen AI) como modelo.

## Pipeline

```
spec.md ──► Analista de Requisitos ──► Desenvolvedor Front-end ──► Revisor QA ──► output/<spec>/
            (plano + RF/RNF + critérios)  (HTML/CSS/JS comentado)    (corrige + rastreabilidade)
```

Saída em `output/<nome-da-spec>/`: os arquivos do programa, `PLANO_TECNICO.md`
e `RELATORIO_RASTREABILIDADE.md` (requisito → código → status).

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

### Criar com linguagem natural

Use `--prompt` para gerar diretamente uma aplicação em linguagem natural, fora do pipeline SDD:

```bash
python main.py --prompt "Crie um gerenciador de tarefas responsivo com prioridade, filtros e persistência local" --abrir
```

O modo não usa o pipeline SDD padrão. A saída fica separada em
`natural_language/<nome-do-prompt>/`, com o site em `index.html` e decisões em
`LIMITACOES.md`, `PEDIDO_NATURAL.md` e `RASTREABILIDADE_NATURAL.md`.

### Avaliar o código

Avalie e corrija automaticamente a geração SDD ou natural mais recente:

```bash
python main.py --avaliar
```

Ou informe um arquivo ou pasta específica:

```bash
python main.py --avaliar output/exemplo_tarefas
python main.py --avaliar output/exemplo_tarefas/script.js
```

O avaliador detecta automaticamente se a geração é SDD ou linguagem natural. O tipo também pode ser escolhido:

```bash
python main.py --avaliar output/exemplo_tarefas --tipo-avaliacao sdd
python main.py --avaliar natural_language/meu_site --tipo-avaliacao natural
```

Os arquivos corrigidos substituem as versões anteriores na própria pasta analisada.
O relatório é gravado como `RELATORIO_AVALIACAO.md` e identifica o tipo avaliado.

### Comparar SDD com linguagem natural

```bash
python main.py --comparar output/exemplo_tarefas natural_language/meu_site
```

O relatório fica em `comparacoes/<sdd>_vs_<natural>/RELATORIO_COMPARATIVO.md`
e não modifica nenhuma das duas pastas originais.

No modo linguagem natural, o relatório pode incluir uma rastreabilidade leve:
`ponto solicitado → implementação → arquivo/linha → status`, sem exigir IDs RF/RNF.

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
output/                    programas gerados por SDD (ignorado pelo git)
natural_language/          programas gerados por linguagem natural (ignorado pelo git)
comparacoes/               relatórios comparativos SDD vs linguagem natural (ignorado pelo git)
```
