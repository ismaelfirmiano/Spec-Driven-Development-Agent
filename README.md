# Spec-Driven-Development-Agent

Trabalho de Engenharia de Software: compara um agente que desenvolve a partir de
uma especificação (SDD) com um agente que desenvolve a partir de um pedido em
linguagem natural. Os dois geram uma aplicação web em HTML, CSS e JavaScript.

## Agentes

1. **Agente SDD**: recebe `entrada.md` (especificação) e gera a aplicação.
2. **Agente natural**: recebe `entrada.txt` (pedido em linguagem natural) e gera a aplicação.
3. **Comparador**: verifica quais requisitos da especificação cada versão atende.

Cada agente roda uma única vez. Não há revisão nem correção do código gerado.
Os dois desenvolvedores usam o mesmo modelo e as mesmas regras técnicas; só muda a
entrada. O comparador recebe as versões como "A" e "B", em ordem sorteada, para
não saber qual é qual.

## Métricas

- Tempo de geração de cada agente.
- Tokens de entrada, de saída e totais.
- Requisitos atendidos, parciais e não atendidos, e a cobertura em %
  (atendido = 1, parcial = 0,5).

## Instalação

Requer Python 3.10 a 3.13.

```bash
./setup.sh
source .venv/bin/activate
```

Coloque sua chave do Gemini no arquivo `.env` (https://aistudio.google.com/apikey).

## Uso

```bash
python main.py
```

Usa `entrada.md` e `entrada.txt`. Para outro par de arquivos com o mesmo nome:

```bash
python main.py specs/taskflow
```

O resultado fica em `resultados/<nome>_<data>/`:

- `sdd/`: aplicação gerada pelo agente SDD
- `natural/`: aplicação gerada pelo agente natural
- `relatorio.md`: métricas, tabela de requisitos e conclusão do comparador

Como o modelo não dá sempre a mesma resposta, rode algumas vezes e compare as médias.

## Entradas disponíveis

| Arquivos | Aplicação |
|---|---|
| `entrada.md` / `entrada.txt` | TodoMVC (cópia de `specs/todomvc`) |
| `specs/todomvc.md` / `.txt` | TodoMVC, adaptado da especificação oficial (github.com/tastejs/todomvc, licença MIT) |
| `specs/taskflow.md` / `.txt` | TaskFlow, gerenciador de tarefas com dashboard e Kanban |
| `specs/uniflow.md` | UniFlow, gestão acadêmica (ainda sem o `.txt`) |

O `.txt` deve pedir a mesma aplicação e as mesmas funcionalidades principais do
`.md`, mas como uma pessoa escreveria, sem lista de requisitos e sem critérios de
aceitação.

## Estrutura

```
main.py                    executa o experimento
agentes/crew.py            agentes, medição e relatório
agentes/config/agents.yaml descrição dos três agentes
agentes/config/tasks.yaml  instruções de cada agente
entrada.md / entrada.txt   entradas padrão
specs/                     outros pares de entrada
tests/                     testes (python -m unittest discover -s tests)
```
