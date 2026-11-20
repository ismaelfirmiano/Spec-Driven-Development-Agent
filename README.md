# Spec-Driven-Development-Agent

Agente de IA que transforma especificações ou pedidos em linguagem natural
em programas web (HTML/CSS/JS) prontos para abrir no navegador. Usa **CrewAI**
para orquestrar agentes especializados e **Gemini** (Google Gen AI) como modelo.

O projeto possui seis agentes especializados:

- **Analista**: transforma especificações em planos técnicos SDD.
- **Desenvolvedor**: implementa o plano em HTML, CSS e JavaScript.
- **Revisor**: corrige e rastreia a implementação SDD.
- **Interpretador**: cria protótipos simples por linguagem natural.
- **Revisor Natural**: revisa o protótipo, deriva requisitos ENF/ERN e evidencia correções prioritárias.
- **Avaliador**: avalia, corrige e compara os modos SDD e natural.

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

## Uso rápido

SDD completo usando os três agentes originais:

```bash
python main.py specs/exemplo_tarefas.md --abrir
```

Linguagem natural:

```bash
python main.py specs/linguagem_natural.md --abrir
python main.py --prompt "Crie uma lista de tarefas simples" --abrir
```

O SDD usa uma geração unificada das Fases 1–3 em uma única implementação,
seguida apenas pela revisão final. Ao concluir, tanto o SDD quanto a linguagem
natural abrem automaticamente o HTML gerado no navegador. Use `--sem-abrir`
para desativar esse comportamento.

Para gerar mais rápido e consumir menos contexto/tokens:

```bash
python main.py specs/exemplo_tarefas.md --rapido --sem-abrir
python main.py --prompt "Crie uma lista de tarefas" --rapido --sem-abrir
```

O modo `--rapido` omite a revisão automática do SDD e da linguagem natural.
A geração continua sendo gravada e pode ser auditada depois com `--avaliar`.

O projeto usa a Gemini API com `gemini-3.8-flash` como principal e modelos Gemini
mais leves como reserva. O modelo `antigravity-preview` foi listado pela API, mas não funciona
com o CrewAI porque não oferece function calling, necessário para os arquivos
estruturados. Se um modelo for incompatível ou indisponível, o agente tenta o
próximo modelo de `SDD_MODELOS_RESERVA`. Veja os disponíveis com:

```bash
python main.py --modelos
```

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
