# Spec-Driven-Development-Agent

Experimento que compara **Spec-Driven Development (SDD)** com **desenvolvimento
por linguagem natural** usando agentes de IA. Os agentes geram programas web
(HTML/CSS/JS) que abrem direto no navegador. Usa **CrewAI** para orquestrar os
agentes e **Gemini** (Google Gen AI) como modelo.

## Desenho do experimento

A pergunta é: *usar SDD gera um código melhor do que pedir em linguagem natural?*
Para a resposta ser válida, **só a forma da entrada muda** entre as duas versões:

```
SDD:      spec.md ──► Analista (plano) ──► Desenvolvedor ──┐
                                                           ├─► Avaliador às cegas ──► RELATORIO_COMPARATIVO.md
Natural:  pedido.md ─────────────────────► Desenvolvedor ──┘   (gabarito = spec SDD)
```

- **Mesmo desenvolvedor:** o mesmo agente, modelo, temperatura e as mesmas regras
  técnicas (`sdd_agent/config/regras_tecnicas.md`) implementam as duas versões.
- **Sem correção automática por padrão:** um agente que revisa e corrige o código
  esconderia a diferença que queremos medir (ele "conserta" justamente o que a
  falta de especificação deixou de fora). A revisão existe como opção
  (`--revisar`), mas, se ligada, é aplicada **igualmente** às duas versões, para
  testar uma segunda hipótese: *a revisão diminui a distância entre SDD e natural?*
- **O avaliador só mede, não corrige.** Ele recebe apenas o código (sem plano,
  relatório ou pedido), com as versões chamadas de "A" e "B" em ordem sorteada.
  A revelação de quem é quem fica no fim do relatório.
- **Gabarito comum:** as duas versões são avaliadas contra a especificação SDD
  completa (o pedido natural descreve o mesmo produto, só que sem o detalhamento
  de requisitos, regras e critérios de aceitação).
- **Métricas objetivas sem LLM** (`sdd_agent/validacao.py`): abre cada versão num
  navegador headless (Playwright), captura erros de JavaScript, verifica arquivos
  referenciados e envio de formulários; conta arquivos e linhas de código.

### Agentes

| Agente | Papel |
|---|---|
| Analista | Transforma a especificação em plano técnico (só no SDD). |
| Desenvolvedor | Implementa a aplicação (o mesmo para SDD e natural). |
| Revisor | Opcional (`--revisar`); revisa e corrige as duas versões da mesma forma. |
| Avaliador | Compara às cegas (`--comparar`) e audita/corrige sob demanda (`--avaliar`). |

## Instalação

> O CrewAI exige **Python ≥3.10 e <3.14**. O `setup.sh` funciona em **macOS e Linux**.

```bash
./setup.sh                 # cria .venv, instala requirements.txt e o Chromium do Playwright
source .venv/bin/activate
# edite .env e coloque sua GEMINI_API_KEY (https://aistudio.google.com/apikey)
```

## Rodando o experimento

Pares prontos de especificação SDD + pedido em linguagem natural:

| Aplicação | Especificação SDD | Pedido natural |
|---|---|---|
| TodoMVC (spec pública, `tastejs/todomvc`, MIT) | `specs/todomvc_sdd.md` (425 linhas) | `specs/natural_todomvc.md` |
| TaskFlow (gerenciador de tarefas completo) | `specs/TaskFlow.md` (598 linhas) | `specs/natural_taskflow.md` |

```bash
python main.py --experimento specs/todomvc_sdd.md specs/natural_todomvc.md
python main.py --experimento specs/TaskFlow.md specs/natural_taskflow.md
python main.py --experimento specs/TaskFlow.md specs/natural_taskflow.md --revisar -o experimentos/taskflow_revisado
```

Saída em `experimentos/<spec>/`: `sdd/`, `natural/` e `RELATORIO_COMPARATIVO.md`
(métricas objetivas, matriz requisito × versão, cobertura, notas por critério e
revelação do cegamento).

Como os LLMs não são determinísticos, rode cada par **várias vezes** (ex.: 3 a 5,
com `-o experimentos/taskflow_1`, `_2`, ...) e compare as médias.

### Passos separados

```bash
python main.py specs/TaskFlow.md --sem-abrir                 # só SDD     -> output/TaskFlow/
python main.py specs/natural_taskflow.md --sem-abrir         # só natural -> natural_language/natural_taskflow/
python main.py --comparar output/TaskFlow natural_language/natural_taskflow --referencia specs/TaskFlow.md
python main.py --prompt "Crie uma lista de tarefas" --abrir  # pedido direto na linha de comando
```

Com um arquivo Markdown, `--modo auto` (padrão) escolhe SDD ou natural pelo
conteúdo; também dá para forçar com `--modo sdd` ou `--modo natural`.

### Escrevendo um pedido natural justo

O pedido natural deve descrever **o mesmo produto e as mesmas funcionalidades
principais** da spec, do jeito que uma pessoa pediria: sem IDs, sem critérios de
aceitação, sem casos-limite e sem contrato de interface. Assim a diferença medida
vem do detalhamento do SDD, e não de funcionalidades omitidas no pedido.

### Auditoria e correção (fora do experimento)

`python main.py --avaliar [caminho]` audita **e corrige** uma geração. Usar isso em
apenas uma das versões invalida a comparação.

## Modelos

Usa `gemini-3.8-flash` como principal e modelos mais leves como reserva
(`SDD_MODELOS_RESERVA`). Veja os disponíveis com `python main.py --modelos`.
`SDD_MAX_TOKENS` (padrão 32768) precisa comportar o código completo de specs grandes.

## Estrutura

```
main.py                          CLI
sdd_agent/crew.py                agentes, etapas, experimento e comparação às cegas
sdd_agent/validacao.py           testes automáticos no navegador (sem LLM)
sdd_agent/config/agents.yaml     papéis dos agentes
sdd_agent/config/tasks.yaml      descrição das etapas
sdd_agent/config/regras_tecnicas.md  regras técnicas comuns às duas versões
specs/                           especificações SDD e pedidos naturais
tests/                           testes unitários (python -m unittest discover -s tests)
experimentos/ output/ natural_language/ comparacoes/   saídas (ignoradas pelo git)
```
