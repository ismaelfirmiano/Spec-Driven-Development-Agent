# Especificação de Funcionalidade: TodoMVC — Lista de Tarefas

**ID da funcionalidade:** 001-todomvc
**Versão:** 1.0.0
**Status:** Pronta para implementação
**Idioma da interface:** Inglês (textos padrão do TodoMVC) — ver seção 9
**Tecnologias:** HTML5, CSS3 e JavaScript puro (ES6+), sem frameworks
**Persistência:** `localStorage`
**Execução:** abrir `index.html` diretamente no navegador (`file://`), sem build e sem servidor

> **Origem e licença.** Esta especificação é uma tradução e adaptação para o
> formato de Spec-Driven Development do *TodoMVC Application Specification*
> (`app-spec.md`, repositório `tastejs/todomvc`, licença MIT —
> https://github.com/tastejs/todomvc/blob/master/app-spec.md), organizada segundo o
> modelo de especificação do GitHub Spec Kit (`templates/spec-template.md`,
> repositório `github/spec-kit`, licença MIT). As regras de comportamento são as do
> TodoMVC original. Foram removidas apenas as exigências ligadas a frameworks,
> npm e à biblioteca de rotas Flatiron Director, que não se aplicam a uma
> aplicação em JavaScript puro aberta por `file://`.

---

## 1. Visão geral

O TodoMVC é uma aplicação de lista de tarefas ("todos") usada como referência
mundial para comparar implementações da mesma aplicação. O usuário cria tarefas,
marca-as como concluídas, edita, exclui, filtra por estado e limpa as concluídas.
Os dados permanecem salvos no navegador.

### 1.1 Objetivos

- **OBJ-01** Permitir o ciclo de vida completo de uma tarefa: criar, concluir,
  reabrir, editar e excluir.
- **OBJ-02** Permitir visualizar todas as tarefas, apenas as ativas ou apenas as
  concluídas, por meio de rotas na URL.
- **OBJ-03** Informar quantas tarefas ainda estão ativas.
- **OBJ-04** Manter os dados e o filtro selecionado após recarregar a página.
- **OBJ-05** Ter comportamento idêntico ao de qualquer outra implementação TodoMVC,
  para permitir comparação justa.

### 1.2 Fora do escopo

- Login, contas de usuário, múltiplas listas.
- Sincronização com servidor, banco de dados remoto ou API.
- Datas, prioridades, categorias, tags, busca textual, ordenação manual ou
  arrastar e soltar.
- Desfazer/refazer.
- Qualquer funcionalidade não descrita nesta especificação.

---

## 2. Histórias de usuário e cenários de aceitação

### História 1 — Criar tarefas (Prioridade: P1)

Como usuário, quero digitar uma tarefa e pressionar Enter para adicioná-la à lista.

**Por que esta prioridade:** sem criar tarefas, nenhuma outra função tem utilidade.

**Teste independente:** abrir a aplicação vazia, digitar um texto e pressionar
Enter; a tarefa deve aparecer na lista.

**Cenários de aceitação:**

1. **Dado** que a página acabou de carregar, **quando** o usuário começa a digitar,
   **então** o texto entra no campo de nova tarefa sem que ele precise clicar nele
   (o campo já está com foco).
2. **Dado** o texto "comprar pão" no campo, **quando** o usuário pressiona Enter,
   **então** a tarefa "comprar pão" é adicionada **ao final** da lista, como ativa,
   e o campo fica vazio.
3. **Dado** o texto "   ler livro   " (com espaços nas pontas), **quando** o usuário
   pressiona Enter, **então** a tarefa é criada com o título "ler livro".
4. **Dado** um campo vazio ou contendo apenas espaços, **quando** o usuário
   pressiona Enter, **então** nenhuma tarefa é criada.
5. **Dado** que existem duas tarefas, **quando** uma terceira é criada, **então**
   ela aparece depois das duas existentes, mantendo a ordem de criação.

### História 2 — Concluir e reabrir tarefas (Prioridade: P1)

Como usuário, quero marcar uma tarefa como concluída e desmarcá-la se mudar de ideia.

**Teste independente:** criar uma tarefa, clicar na caixa de seleção e verificar o
estilo de concluída; clicar novamente e verificar que voltou a ativa.

**Cenários de aceitação:**

1. **Dado** uma tarefa ativa, **quando** o usuário clica na sua caixa de seleção,
   **então** a tarefa passa a concluída e o item recebe a classe `completed`
   (exibido com texto riscado e esmaecido).
2. **Dado** uma tarefa concluída, **quando** o usuário clica na sua caixa de
   seleção, **então** ela volta a ativa e a classe `completed` é removida.
3. **Dado** qualquer mudança de estado, **então** o contador de tarefas ativas é
   atualizado imediatamente.

### História 3 — Marcar todas como concluídas (Prioridade: P2)

Como usuário, quero concluir (ou reabrir) todas as tarefas com um único clique.

**Cenários de aceitação:**

1. **Dado** tarefas ativas e concluídas misturadas, **quando** o usuário marca a
   caixa "Mark all as complete", **então** todas as tarefas ficam concluídas.
2. **Dado** que todas estão concluídas e a caixa "Mark all as complete" está
   marcada, **quando** o usuário a desmarca, **então** todas voltam a ativas.
3. **Dado** tarefas ativas, **quando** o usuário conclui uma a uma até a última,
   **então** a caixa "Mark all as complete" fica marcada automaticamente.
4. **Dado** que todas estão concluídas, **quando** o usuário reabre uma única
   tarefa, **então** a caixa "Mark all as complete" fica desmarcada
   automaticamente.
5. **Dado** que a caixa "Mark all as complete" está marcada, **quando** o usuário
   clica em "Clear completed", **então** a caixa fica desmarcada.

### História 4 — Editar tarefas (Prioridade: P1)

Como usuário, quero corrigir o texto de uma tarefa com duplo clique.

**Cenários de aceitação:**

1. **Dado** uma tarefa, **quando** o usuário dá duplo clique no seu texto,
   **então** o item entra em modo de edição (classe `editing` no `<li>`), os outros
   controles do item (caixa de seleção e botão de excluir) ficam ocultos, e aparece
   um campo de texto com o título atual, **já com foco**.
2. **Dado** o modo de edição, **quando** o usuário altera o texto e pressiona
   Enter, **então** o novo título é salvo e o modo de edição termina.
3. **Dado** o modo de edição, **quando** o campo perde o foco (blur), **então** o
   novo título é salvo e o modo de edição termina.
4. **Dado** o modo de edição, **quando** o texto tem espaços nas pontas, **então**
   o título salvo é o texto sem esses espaços.
5. **Dado** o modo de edição, **quando** o usuário apaga todo o texto (ou deixa
   apenas espaços) e confirma com Enter ou blur, **então** a tarefa é **excluída**.
6. **Dado** o modo de edição, **quando** o usuário pressiona Escape, **então** o
   modo de edição termina e **as alterações são descartadas** (o título anterior
   permanece).
7. **Dado** que a edição foi cancelada com Escape, **então** o evento de blur que
   ocorre em seguida **não** pode salvar o texto descartado.
8. **Dado** uma edição confirmada com Enter, **então** o blur que ocorre em seguida
   não pode gerar uma segunda gravação nem erro.

### História 5 — Excluir tarefas (Prioridade: P1)

Como usuário, quero remover uma tarefa que não preciso mais.

**Cenários de aceitação:**

1. **Dado** uma tarefa, **quando** o mouse passa sobre ela, **então** aparece o
   botão de excluir (×, classe `destroy`).
2. **Dado** o botão de excluir visível, **quando** o usuário clica nele, **então**
   a tarefa é removida da lista e do armazenamento.
3. **Dado** a exclusão da última tarefa, **então** a seção principal e o rodapé
   ficam ocultos.

### História 6 — Contador de tarefas ativas (Prioridade: P2)

**Cenários de aceitação:**

1. **Dado** 0 tarefas ativas (e pelo menos uma concluída), **então** o rodapé
   mostra "**0** items left".
2. **Dado** 1 tarefa ativa, **então** mostra "**1** item left" (singular).
3. **Dado** 2 ou mais tarefas ativas, **então** mostra "**N** items left" (plural).
4. O número fica dentro de um elemento `<strong>`.
5. O contador considera **todas** as tarefas ativas, independentemente do filtro
   selecionado.

### História 7 — Limpar concluídas (Prioridade: P2)

**Cenários de aceitação:**

1. **Dado** pelo menos uma tarefa concluída, **então** o botão "Clear completed"
   está visível no rodapé.
2. **Dado** nenhuma tarefa concluída, **então** o botão "Clear completed" está
   oculto.
3. **Dado** tarefas concluídas, **quando** o usuário clica em "Clear completed",
   **então** todas as concluídas são removidas e as ativas permanecem, na mesma
   ordem.

### História 8 — Filtrar por rotas (Prioridade: P1)

Como usuário, quero ver todas as tarefas, só as ativas ou só as concluídas.

**Cenários de aceitação:**

1. **Dado** a URL terminando em `#/` (ou sem fragmento), **então** todas as
   tarefas são exibidas e o link "All" está selecionado.
2. **Dado** a URL `#/active`, **então** só as tarefas ativas são exibidas e o link
   "Active" está selecionado.
3. **Dado** a URL `#/completed`, **então** só as concluídas são exibidas e o link
   "Completed" está selecionado.
4. O link selecionado tem a classe `selected`; os outros não.
5. **Dado** o filtro "Active", **quando** o usuário conclui uma tarefa, **então**
   ela desaparece imediatamente da lista visível.
6. **Dado** o filtro "Completed", **quando** o usuário reabre uma tarefa, **então**
   ela desaparece imediatamente da lista visível.
7. **Dado** o filtro "Active", **quando** o usuário cria uma tarefa, **então** ela
   aparece (é ativa); **dado** o filtro "Completed", a tarefa é criada, mas não
   aparece até o filtro mudar.
8. **Dado** um filtro selecionado, **quando** a página é recarregada, **então** o
   mesmo filtro continua aplicado.
9. Os botões voltar/avançar do navegador trocam o filtro de acordo com a URL.
10. O filtro é aplicado sobre os dados (modelo), não apenas escondendo elementos
    com CSS.

### História 9 — Persistência (Prioridade: P1)

**Cenários de aceitação:**

1. **Dado** tarefas criadas, concluídas, editadas ou excluídas, **quando** a página
   é recarregada, **então** a lista aparece exatamente como estava.
2. **Dado** uma tarefa em modo de edição, **quando** a página é recarregada,
   **então** ela aparece fora do modo de edição (o modo de edição não é salvo).
3. **Dado** que não há dados salvos, **então** a aplicação inicia com a lista vazia,
   sem erros.
4. **Dado** que o valor salvo está corrompido (JSON inválido), **então** a aplicação
   inicia com a lista vazia, sem quebrar e sem erros não tratados no console.

---

## 3. Casos-limite

- **CL-01** Pressionar Enter várias vezes seguidas com o campo vazio não cria nada.
- **CL-02** Títulos com caracteres especiais ou HTML (ex.: `<b>oi</b>`,
  `<img src=x onerror=alert(1)>`) são exibidos como texto literal, nunca
  interpretados como HTML.
- **CL-03** Títulos longos quebram linha sem estourar o layout.
- **CL-04** Concluir todas as tarefas no filtro "Active" deixa a lista visível
  vazia, mas o rodapé continua visível (há tarefas no total).
- **CL-05** "Mark all as complete" com o filtro "Active" afeta **todas** as
  tarefas, não apenas as visíveis.
- **CL-06** Excluir uma tarefa durante a edição de outra não deve perder a edição
  em andamento nem gerar erro.
- **CL-07** Rota desconhecida (ex.: `#/xyz`) é tratada como "All".

---

## 4. Requisitos funcionais

- **FR-001** O sistema DEVE ocultar a seção principal (`#main` / `.main`) e o
  rodapé (`#footer` / `.footer`) quando não houver nenhuma tarefa.
- **FR-002** O sistema DEVE exibir no topo um campo de nova tarefa com foco
  automático ao carregar a página (preferencialmente atributo `autofocus`).
- **FR-003** O sistema DEVE criar a tarefa ao pressionar Enter, adicioná-la ao
  final da lista e limpar o campo.
- **FR-004** O sistema DEVE aplicar `trim()` ao título e rejeitar títulos vazios
  na criação.
- **FR-005** Cada tarefa DEVE ter uma caixa de seleção que alterna seu estado
  `completed` e a classe `completed` no `<li>` correspondente.
- **FR-006** O sistema DEVE oferecer a caixa "Mark all as complete" que coloca
  todas as tarefas no mesmo estado que ela.
- **FR-007** A caixa "Mark all as complete" DEVE refletir automaticamente se todas
  as tarefas estão concluídas, e DEVE ser desmarcada após "Clear completed".
- **FR-008** Duplo clique no rótulo (`<label>`) de uma tarefa DEVE ativar o modo
  de edição, adicionando a classe `editing` ao `<li>`.
- **FR-009** No modo de edição, o sistema DEVE ocultar os outros controles do item
  e mostrar um campo com o título atual, com foco (`.focus()`).
- **FR-010** A edição DEVE ser salva ao pressionar Enter e ao perder o foco (blur),
  removendo a classe `editing`.
- **FR-011** Na edição, o título DEVE passar por `trim()`; se ficar vazio, a tarefa
  DEVE ser excluída.
- **FR-012** Pressionar Escape durante a edição DEVE sair do modo de edição e
  descartar as alterações.
- **FR-013** Passar o mouse sobre uma tarefa DEVE exibir o botão de excluir
  (`.destroy`), que remove a tarefa ao ser clicado.
- **FR-014** O rodapé DEVE exibir o número de tarefas ativas dentro de `<strong>`,
  com pluralização correta: "0 items", "1 item", "2 items" seguidos de "left".
- **FR-015** O botão "Clear completed" DEVE remover todas as tarefas concluídas e
  DEVE ficar oculto quando não houver tarefas concluídas.
- **FR-016** O sistema DEVE persistir as tarefas dinamicamente no `localStorage`
  a cada alteração, usando para cada item as chaves `id`, `title` e `completed`.
- **FR-017** A chave do `localStorage` DEVE seguir o formato `todos-[framework]`;
  nesta implementação, `todos-vanillajs`.
- **FR-018** O estado de edição NÃO DEVE ser persistido.
- **FR-019** O sistema DEVE implementar as rotas `#/` (todas — padrão),
  `#/active` e `#/completed` (`#!/` também é aceito), usando o evento
  `hashchange` do navegador.
- **FR-020** Ao mudar a rota, a lista DEVE ser filtrada no nível dos dados e a
  classe `selected` DEVE ser alternada nos links de filtro.
- **FR-021** Quando uma tarefa for alterada com um filtro ativo, a lista DEVE ser
  atualizada conforme o filtro (ex.: concluir no filtro "Active" esconde a tarefa).
- **FR-022** O filtro ativo DEVE ser mantido ao recarregar a página.
- **FR-023** Os títulos das tarefas DEVEM ser inseridos no DOM como texto
  (`textContent`), nunca como HTML.
- **FR-024** Dados ausentes ou corrompidos no `localStorage` NÃO DEVEM impedir a
  aplicação de iniciar.

### 4.1 Entidades

- **Todo** — representa uma tarefa.
  - `id`: identificador único e estável (string ou número), gerado na criação;
    não depende da posição na lista.
  - `title`: texto não vazio, já sem espaços nas pontas.
  - `completed`: booleano; `false` na criação.
- **Filtro** — um de `all`, `active`, `completed`; derivado da URL.

---

## 5. Interface

A estrutura visual segue o modelo oficial do TodoMVC (`todomvc-app-template`),
que deve ser reproduzido o mais fielmente possível:

```
<section class="todoapp">
  <header class="header">
    <h1>todos</h1>
    <input class="new-todo" placeholder="What needs to be done?" autofocus>
  </header>
  <!-- oculto quando não há tarefas -->
  <section class="main">
    <input id="toggle-all" class="toggle-all" type="checkbox">
    <label for="toggle-all">Mark all as complete</label>
    <ul class="todo-list">
      <!-- cada tarefa:
      <li [class="completed"] [class="editing"]>
        <div class="view">
          <input class="toggle" type="checkbox" [checked]>
          <label>Título</label>
          <button class="destroy"></button>
        </div>
        <input class="edit" value="Título">
      </li> -->
    </ul>
  </section>
  <!-- oculto quando não há tarefas -->
  <footer class="footer">
    <span class="todo-count"><strong>0</strong> items left</span>
    <ul class="filters">
      <li><a class="selected" href="#/">All</a></li>
      <li><a href="#/active">Active</a></li>
      <li><a href="#/completed">Completed</a></li>
    </ul>
    <!-- oculto quando não há concluídas -->
    <button class="clear-completed">Clear completed</button>
  </footer>
</section>
<footer class="info">
  <p>Double-click to edit a todo</p>
</footer>
```

- **UI-01** O título "todos" aparece grande e centralizado no topo.
- **UI-02** O campo de nova tarefa mostra o placeholder "What needs to be done?".
- **UI-03** Tarefas concluídas aparecem com texto riscado e cor esmaecida.
- **UI-04** O botão de excluir só aparece ao passar o mouse sobre o item.
- **UI-05** O layout é centralizado, com largura máxima em torno de 550 px, e
  utilizável em telas de celular.
- **UI-06** O rodapé informativo mostra "Double-click to edit a todo".

---

## 6. Requisitos não funcionais

- **NFR-01 Execução local:** abre com duplo clique em `index.html` (`file://`), sem
  módulos ES, sem build, sem servidor e sem bibliotecas externas.
- **NFR-02 Estrutura:** separar HTML, CSS e JavaScript em arquivos próprios
  (sugestão: `index.html`, `css/app.css`, `js/app.js`; componentes podem ser
  divididos em arquivos, carregados como scripts clássicos na ordem correta).
- **NFR-03 Estilo de código:** aspas duplas no HTML e simples em JS/CSS; usar
  constantes nomeadas para teclas (ex.: `const ENTER_KEY = 'Enter'`,
  `const ESCAPE_KEY = 'Escape'`) em vez de valores soltos.
- **NFR-04 Sem pré-processadores:** nada de Sass, TypeScript ou CoffeeScript.
- **NFR-05 Compatibilidade:** funcionar nas versões atuais de Chrome, Firefox,
  Safari e Edge.
- **NFR-06 Segurança:** nenhum conteúdo do usuário é inserido via `innerHTML`,
  `outerHTML` ou `document.write`.
- **NFR-07 Acessibilidade:** controles com rótulos acessíveis (o campo de nova
  tarefa e a caixa "Mark all as complete" precisam de rótulo ou `aria-label`),
  foco visível e operação por teclado para criar, concluir e editar.
- **NFR-08 Desempenho:** a interface responde sem atraso perceptível com até 500
  tarefas.
- **NFR-09 Robustez:** nenhum erro de JavaScript no console durante o uso normal.

---

## 7. Critérios de sucesso

- **SC-001** Todos os cenários de aceitação das histórias 1 a 9 são satisfeitos.
- **SC-002** Nenhum erro de JavaScript no console ao abrir a página e ao executar
  cada cenário.
- **SC-003** Após recarregar a página, as tarefas e o filtro são idênticos ao
  estado anterior.
- **SC-004** Um título contendo HTML é exibido literalmente (CL-02).
- **SC-005** Nenhuma funcionalidade fora do escopo (seção 1.2) é adicionada.

---

## 8. Premissas

- O usuário usa um navegador moderno com `localStorage` habilitado.
- Uma única lista por navegador.
- Sem limite rígido de quantidade de tarefas, além do limite do `localStorage`.

## 9. Observação sobre idioma

Os textos da interface seguem o TodoMVC original, em inglês ("todos", "What needs
to be done?", "items left", "All", "Active", "Completed", "Clear completed",
"Mark all as complete", "Double-click to edit a todo"), para manter a aplicação
comparável às demais implementações TodoMVC.

## 10. Matriz de rastreabilidade (requisito → cenário)

| Requisito | Cenários |
|---|---|
| FR-001 | H5.3, H9.3 |
| FR-002 | H1.1 |
| FR-003 | H1.2, H1.5 |
| FR-004 | H1.3, H1.4, CL-01 |
| FR-005 | H2.1, H2.2 |
| FR-006 | H3.1, H3.2, CL-05 |
| FR-007 | H3.3, H3.4, H3.5 |
| FR-008 | H4.1 |
| FR-009 | H4.1 |
| FR-010 | H4.2, H4.3, H4.8 |
| FR-011 | H4.4, H4.5 |
| FR-012 | H4.6, H4.7 |
| FR-013 | H5.1, H5.2 |
| FR-014 | H6.1–H6.5 |
| FR-015 | H7.1–H7.3 |
| FR-016 | H9.1 |
| FR-017 | H9.1 |
| FR-018 | H9.2 |
| FR-019 | H8.1–H8.3, H8.9, CL-07 |
| FR-020 | H8.4, H8.10 |
| FR-021 | H8.5–H8.7, CL-04 |
| FR-022 | H8.8 |
| FR-023 | CL-02 |
| FR-024 | H9.3, H9.4 |
