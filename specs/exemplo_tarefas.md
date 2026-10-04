# Especificação: Lista de Tarefas

## Objetivo
Aplicação web simples para organizar tarefas pessoais, rodando inteiramente no
navegador.

## Requisitos funcionais
- **RF-01** O usuário pode adicionar uma tarefa digitando um título e
  pressionando Enter ou clicando em "Adicionar". Títulos vazios são ignorados.
- **RF-02** O usuário pode marcar e desmarcar uma tarefa como concluída;
  tarefas concluídas aparecem riscadas.
- **RF-03** O usuário pode excluir uma tarefa.
- **RF-04** Filtros "Todas", "Pendentes" e "Concluídas".
- **RF-05** Um contador mostra quantas tarefas estão pendentes.
- **RF-06** As tarefas persistem ao recarregar a página (localStorage).

## Requisitos não funcionais
- **RNF-01** Interface responsiva, utilizável em celular (largura ≥ 360px).
- **RNF-02** Interface em português do Brasil.
- **RNF-03** Sem dependências externas.

## Fora do escopo
- Login, sincronização entre dispositivos, datas de vencimento.
