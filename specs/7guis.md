# Especificação: 7GUIs — Sete Tarefas de Interface Gráfica

**Versão:** 1.0.0
**Tipo:** Aplicação web com sete ferramentas independentes
**Idioma da interface:** Português
**Tecnologias:** HTML5, CSS3 e JavaScript puro, sem frameworks e sem bibliotecas externas
**Execução:** abrir `index.html` direto no navegador (`file://`), sem servidor e sem build

> **Origem.** Baseada no 7GUIs, de Eugen Kiss (https://eugenkiss.github.io/7guis/tasks,
> repositório `eugenkiss/7guis`), um benchmark acadêmico usado para comparar a
> facilidade de programar interfaces gráficas. Ele propõe sete tarefas em ordem
> crescente de dificuldade: contador, conversor de temperatura, reserva de voos,
> temporizador, CRUD, desenho de círculos com desfazer/refazer e planilha. O site
> original deixa alguns detalhes em aberto (formato de data, valores do slider,
> linguagem de fórmulas da planilha). Nesta especificação eles foram definidos; a
> linguagem de fórmulas segue o exemplo SCells do livro *Programming in Scala*,
> citado pelo próprio 7GUIs.

---

## 1. Estrutura geral

- **GER-01** A página tem um menu (abas ou barra lateral) com as sete tarefas:
  Contador, Temperatura, Voos, Temporizador, CRUD, Círculos e Planilha.
- **GER-02** Só uma tarefa aparece por vez; trocar de tarefa não recarrega a página.
- **GER-03** A tarefa aberta fica destacada no menu e é mantida na URL (`#/contador`,
  `#/temperatura`, `#/voos`, `#/temporizador`, `#/crud`, `#/circulos`, `#/planilha`);
  recarregar a página reabre a mesma tarefa. Sem fragmento, abre o Contador.
- **GER-04** Cada tarefa mantém seu estado ao trocar de aba e voltar, enquanto a
  página não for recarregada. Não há persistência entre recarregamentos.
- **GER-05** O código de cada tarefa fica separado (arquivo ou módulo próprio); na
  planilha, a lógica de fórmulas fica separada da interface.

---

## 2. Tarefa 1 — Contador

- **CON-01** Mostra um campo somente leitura com o valor atual e um botão "Contar".
- **CON-02** O valor começa em 0.
- **CON-03** Cada clique em "Contar" soma 1 ao valor.

**Critério:** após 3 cliques, o campo mostra 3.

---

## 3. Tarefa 2 — Conversor de temperatura

- **TEM-01** Mostra dois campos de texto, "Celsius" e "Fahrenheit", ambos vazios no início.
- **TEM-02** Ao digitar um número válido em Celsius, Fahrenheit é atualizado na
  hora, a cada tecla: F = C × 9/5 + 32.
- **TEM-03** Ao digitar um número válido em Fahrenheit, Celsius é atualizado na
  hora: C = (F − 32) × 5/9.
- **TEM-04** São aceitos números negativos e decimais com ponto ou vírgula
  (ex.: `-40`, `36,6`, `98.6`).
- **TEM-05** Se o texto digitado não for um número, o outro campo **não** muda e o
  campo inválido fica com borda vermelha e uma mensagem "valor inválido".
- **TEM-06** O valor calculado é exibido com no máximo 2 casas decimais, sem zeros
  desnecessários (ex.: `37`, `98.6`, `-17.78`).
- **TEM-07** Apagar todo o conteúdo de um campo limpa o outro campo.

**Critérios:** 100 °C → 212 °F; −40 °C → −40 °F; 98.6 °F → 37 °C; digitar "abc"
em Celsius mantém o valor anterior de Fahrenheit.

---

## 4. Tarefa 3 — Reserva de voos

- **VOO-01** Mostra uma lista de seleção com "voo só de ida" e "voo de ida e volta",
  dois campos de data (ida e volta) e o botão "Reservar".
- **VOO-02** Estado inicial: "voo só de ida" selecionado; os dois campos com a data
  de hoje; o campo de volta desabilitado.
- **VOO-03** As datas são digitadas no formato `dd.mm.aaaa` (ex.: `27.03.2026`).
- **VOO-04** O campo de volta fica habilitado se, e somente se, "voo de ida e volta"
  estiver selecionado.
- **VOO-05** Um campo habilitado com data mal formatada ou inexistente (ex.:
  `31.02.2026`) fica com fundo vermelho e o botão "Reservar" fica desabilitado.
- **VOO-06** O campo de volta, quando desabilitado, não é validado: não fica
  vermelho e não desabilita o botão.
- **VOO-07** Em "ida e volta", se a data de volta for anterior à de ida, o botão
  fica desabilitado (data igual é permitida).
- **VOO-08** A validação ocorre a cada tecla.
- **VOO-09** Ao clicar em "Reservar", aparece uma mensagem de confirmação:
  - ida: "Você reservou um voo só de ida para 27.03.2026."
  - ida e volta: "Você reservou um voo de ida e volta: ida em 27.03.2026 e volta
    em 05.04.2026."
- **VOO-10** A mensagem é exibida na própria página (sem `alert`).

---

## 5. Tarefa 4 — Temporizador

- **TMP-01** Mostra uma barra de progresso do tempo decorrido, um texto com o tempo
  decorrido em segundos com uma casa decimal (ex.: "3.4 s"), um controle deslizante
  de duração e o botão "Reiniciar".
- **TMP-02** O controle deslizante vai de 1 a 30 segundos e começa em 10 s; o valor
  escolhido aparece ao lado dele.
- **TMP-03** O temporizador começa a contar ao abrir a tarefa pela primeira vez, e
  atualiza a tela pelo menos 10 vezes por segundo.
- **TMP-04** Enquanto decorrido < duração, o tempo decorrido aumenta.
- **TMP-05** Quando decorrido ≥ duração, a contagem para e a barra fica cheia.
- **TMP-06** Mexer no controle deslizante atualiza a duração e a barra
  **durante** o arraste, não só ao soltar.
- **TMP-07** Se a duração aumentar para um valor maior que o decorrido, a contagem
  recomeça de onde parou até alcançar a nova duração.
- **TMP-08** Se a duração diminuir para um valor menor que o decorrido, a contagem
  para e a barra fica cheia.
- **TMP-09** "Reiniciar" zera o tempo decorrido (a duração não muda) e a contagem
  recomeça.
- **TMP-10** O tempo decorrido usa o relógio real (ex.: `performance.now()`), sem
  acumular atraso de `setInterval`.

---

## 6. Tarefa 5 — CRUD de nomes

- **CRU-01** Mostra: campo "Filtrar por sobrenome", campos "Nome" e "Sobrenome",
  uma lista de pessoas e os botões "Criar", "Atualizar" e "Excluir".
- **CRU-02** A lista começa com três pessoas: "Emil, Hans", "Mustermann, Max" e
  "Tisch, Roman" (formato "Sobrenome, Nome").
- **CRU-03** Só uma pessoa pode estar selecionada por vez; selecionar uma pessoa
  preenche os campos Nome e Sobrenome com os dados dela.
- **CRU-04** Digitar no filtro atualiza a lista na hora, mostrando só as pessoas
  cujo sobrenome começa com o texto digitado, sem diferenciar maiúsculas.
- **CRU-05** "Criar" adiciona uma pessoa com o nome e o sobrenome dos campos ao
  final da lista.
- **CRU-06** "Criar" fica desabilitado se Nome ou Sobrenome estiver vazio (ou só
  com espaços).
- **CRU-07** "Atualizar" e "Excluir" ficam habilitados se, e somente se, houver uma
  pessoa selecionada.
- **CRU-08** "Atualizar" substitui a pessoa selecionada pelos dados dos campos, na
  mesma posição; não cria uma nova.
- **CRU-09** "Excluir" remove a pessoa selecionada e deixa a lista sem seleção.
- **CRU-10** Se o filtro esconder a pessoa selecionada, a seleção é desfeita.
- **CRU-11** A lista ocupa todo o espaço vertical que sobrar na tarefa.
- **CRU-12** A lista funciona por teclado (setas para mudar a seleção).

---

## 7. Tarefa 6 — Desenho de círculos

- **CIR-01** Mostra os botões "Desfazer" e "Refazer" e uma área de desenho abaixo
  deles (mínimo 600 × 400 px em telas grandes).
- **CIR-02** Clicar com o botão esquerdo em um ponto vazio cria um círculo sem
  preenchimento, com diâmetro de 30 px, centrado no clique.
- **CIR-03** O círculo selecionado é o mais próximo do ponteiro entre os que
  contêm o ponteiro (distância ao centro menor que o raio). Ele aparece preenchido
  de cinza. Se o ponteiro não estiver sobre nenhum círculo, nenhum fica selecionado.
- **CIR-04** Clicar com o botão esquerdo sobre um círculo não cria outro.
- **CIR-05** Clicar com o botão direito sobre o círculo selecionado abre um menu
  com a única opção "Ajustar diâmetro..." (o menu do navegador não aparece).
- **CIR-06** Essa opção abre uma janela (diálogo na página) com um controle
  deslizante de diâmetro, de 5 a 200 px, começando no diâmetro atual. O círculo
  muda **na hora** enquanto o controle é arrastado.
- **CIR-07** Ao fechar o diálogo, o ajuste conta como **uma** alteração para
  desfazer/refazer, mesmo que o controle tenha sido movido várias vezes. Se o
  diâmetro final for igual ao inicial, nada é registrado.
- **CIR-08** Enquanto o diálogo está aberto, a área de desenho não aceita cliques.
- **CIR-09** São alterações desfazíveis: criar um círculo e ajustar um diâmetro.
- **CIR-10** "Desfazer" reverte a última alteração; "Refazer" reaplica a última
  alteração desfeita.
- **CIR-11** Fazer uma alteração nova depois de desfazer apaga o histórico de refazer.
- **CIR-12** "Desfazer" fica desabilitado sem nada para desfazer; "Refazer" fica
  desabilitado sem nada para refazer.

**Critério:** criar 2 círculos, ajustar o diâmetro do primeiro de 30 para 80,
desfazer (primeiro volta a 30), desfazer (segundo some), refazer (segundo volta),
criar um terceiro círculo (Refazer fica desabilitado).

---

## 8. Tarefa 7 — Planilha

### 8.1 Grade

- **PLA-01** Grade com colunas A a Z (26) e linhas 0 a 99 (100), com cabeçalhos de
  coluna e de linha fixos durante a rolagem.
- **PLA-02** A grade rola horizontal e verticalmente dentro da área da tarefa.
- **PLA-03** Cada célula mostra o **valor** calculado, não a fórmula.
- **PLA-04** Dar duplo clique em uma célula (ou pressionar Enter com ela
  selecionada) abre a edição, mostrando o conteúdo digitado (a fórmula).
- **PLA-05** Enter ou sair da célula confirma a edição; Esc cancela e mantém o
  conteúdo anterior.
- **PLA-06** Não usar componente pronto de planilha; a grade é construída com
  elementos HTML (tabela ou equivalente).

### 8.2 Conteúdo das células

- **PLA-07** Célula vazia vale 0 quando usada em fórmulas e aparece em branco.
- **PLA-08** Conteúdo que é um número (ex.: `12`, `-3.5`) vale esse número.
- **PLA-09** Conteúdo que não começa com `=` e não é número é texto, exibido como
  está; quando usado em fórmulas, vale 0.
- **PLA-10** Conteúdo que começa com `=` é uma fórmula.

### 8.3 Linguagem de fórmulas

Gramática (espaços entre os elementos são ignorados):

```
formula  := "=" expr
expr     := numero | celula | funcao
celula   := letra(A-Z) digitos(0-99)          ex.: A1, B12, Z99
faixa    := celula ":" celula                  ex.: A1:B5
funcao   := nome "(" args ")"
args     := arg ("," arg)*
arg      := expr | faixa
nome     := add | sub | mul | div | sum | prod   (sem diferenciar maiúsculas)
```

- **PLA-11** `add(a, b)` soma, `sub(a, b)` subtrai, `mul(a, b)` multiplica,
  `div(a, b)` divide (exatamente 2 argumentos).
- **PLA-12** `sum(...)` soma e `prod(...)` multiplica todos os argumentos, que podem
  ser números, células, faixas ou outras funções, em qualquer quantidade (≥ 1).
- **PLA-13** Uma faixa `A1:B3` inclui todas as células do retângulo entre os dois
  cantos, inclusive; a ordem dos cantos não importa (`B3:A1` é igual).
- **PLA-14** Funções podem ser aninhadas: `=add(A1, mul(B2, 3))`.
- **PLA-15** Exemplos: `=A1`, `=5`, `=sum(A0:A9)`, `=div(sum(B1:B4), 4)`.

### 8.4 Erros

- **PLA-16** Fórmula com sintaxe inválida, função desconhecida, número errado de
  argumentos ou célula fora da grade mostra `#ERRO` na célula.
- **PLA-17** Divisão por zero mostra `#DIV/0`.
- **PLA-18** Referência circular (direta, `A1` = `=A1`, ou indireta, `A1` → `B1` →
  `A1`) mostra `#CICLO` em todas as células do ciclo, sem travar a página.
- **PLA-19** Uma fórmula que usa uma célula com erro também mostra erro.
- **PLA-20** Corrigir a célula que causou o erro faz as dependentes voltarem a
  mostrar valores.

### 8.5 Propagação

- **PLA-21** Ao confirmar a edição de uma célula, todas as células que dependem
  dela (direta ou indiretamente) são recalculadas e atualizadas na tela.
- **PLA-22** Só são recalculadas as células afetadas, não a grade inteira.
- **PLA-23** A lógica de fórmulas (análise, cálculo e dependências) fica separada
  do código da interface.
- **PLA-24** Números são exibidos sem zeros desnecessários e com no máximo 10
  dígitos significativos (ex.: `0.3333333333`).

**Critérios:** A0=`2`, A1=`3`, A2=`=add(A0,A1)` mostra 5; mudar A0 para `10` faz A2
mostrar 13; B0=`=sum(A0:A2)` mostra 26; C0=`=div(A0, D0)` com D0 vazio mostra
`#DIV/0`; A0=`=A2` cria um ciclo e A0 e A2 mostram `#CICLO`.

---

## 9. Requisitos não funcionais

- **RNF-01** Abre com duplo clique em `index.html`, sem servidor, módulos ES ou build.
- **RNF-02** Nenhum erro de JavaScript no console durante o uso normal.
- **RNF-03** Conteúdo digitado pelo usuário é exibido como texto (`textContent`),
  nunca interpretado como HTML.
- **RNF-04** Todos os controles têm rótulos acessíveis e funcionam por teclado
  (exceto o desenho de círculos, que depende do mouse).
- **RNF-05** Layout utilizável em telas de 360 px de largura; a planilha e a área
  de desenho podem rolar.
- **RNF-06** A planilha responde sem atraso perceptível ao editar uma célula com
  100 células dependentes.
