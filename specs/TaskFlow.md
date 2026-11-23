SDD — TaskFlow

Sistema Web de Gerenciamento de Tarefas

Versão: 1.0
Tipo: Aplicação web responsiva
Idioma da interface: Português brasileiro
Tecnologias obrigatórias: HTML5, CSS3 e JavaScript ES6+
Persistência: localStorage
Objetivo: Avaliar a capacidade de um agente de IA de projetar, implementar e testar uma aplicação web funcional a partir de requisitos detalhados.

---

1. Visão geral

O TaskFlow é uma aplicação web que permite ao usuário cadastrar, visualizar, editar, organizar, pesquisar, filtrar e concluir tarefas pessoais.

A aplicação deverá funcionar localmente em um navegador moderno, sem exigir cadastro, servidor ou banco de dados externo.

Os dados deverão permanecer disponíveis após recarregar a página ou fechar e reabrir o navegador, desde que o armazenamento local não seja apagado.

O sistema deverá apresentar uma interface intuitiva, acessível, responsiva e consistente.

2. Objetivos do sistema

1. Centralizar tarefas em uma única interface.
2. Permitir o gerenciamento completo do ciclo de vida de uma tarefa.
3. Facilitar a localização de tarefas por texto, status, prioridade e categoria.
4. Apresentar indicadores atualizados sobre o andamento das atividades.
5. Garantir a persistência local dos dados.
6. Impedir entradas inválidas e operações inconsistentes.
7. Permitir testes automatizados das funcionalidades principais.

3. Escopo

3.1 Funcionalidades incluídas

- Dashboard com indicadores.
- Cadastro de tarefas.
- Edição de tarefas.
- Exclusão com confirmação.
- Conclusão e reabertura de tarefas.
- Pesquisa por texto.
- Filtros combináveis.
- Ordenação.
- Visualização em lista e quadro Kanban.
- Categorias e prioridades.
- Datas de vencimento.
- Persistência com localStorage.
- Exportação e importação de dados em JSON.
- Alternância entre tema claro e escuro.
- Layout responsivo.
- Tratamento de erros e estados vazios.

3.2 Funcionalidades excluídas

- Login e autenticação.
- Compartilhamento entre usuários.
- Sincronização em nuvem.
- Notificações enviadas por servidor.
- Banco de dados remoto.
- Colaboração em tempo real.

O agente não deverá implementar funcionalidades fora do escopo sem justificar a necessidade e solicitar autorização.

4. Requisitos funcionais

RF-001 — Dashboard

O sistema deverá apresentar:

- Quantidade total de tarefas.
- Quantidade de tarefas pendentes.
- Quantidade de tarefas em andamento.
- Quantidade de tarefas concluídas.
- Quantidade de tarefas atrasadas.
- Percentual de conclusão.

Os indicadores deverão ser calculados a partir dos dados armazenados, sem valores fixos inseridos manualmente no código.

O percentual de conclusão será calculado por:

percentual = tarefas concluídas / total de tarefas × 100.

Se não houver tarefas, o percentual deverá ser zero.

RF-002 — Cadastro de tarefas

O usuário deverá conseguir criar uma tarefa informando:

- Título, obrigatório, entre 3 e 100 caracteres.
- Descrição, opcional, com até 1.000 caracteres.
- Categoria, selecionada entre as categorias disponíveis.
- Prioridade: baixa, média, alta ou urgente.
- Status: pendente, em andamento ou concluída.
- Data de vencimento, opcional.
- Data de criação, gerada automaticamente.

O sistema deverá validar os campos antes de salvar.

Títulos contendo apenas espaços deverão ser rejeitados.

Após o cadastro válido, a tarefa deverá aparecer imediatamente na interface e ser persistida.

RF-003 — Identificação única

Cada tarefa deverá possuir um identificador único e estável.

A identificação não poderá depender da posição da tarefa na lista, pois a ordem poderá mudar após filtros, exclusões ou ordenações.

RF-004 — Edição de tarefas

O usuário deverá conseguir editar qualquer campo permitido de uma tarefa existente.

O formulário deverá ser preenchido com os valores atuais.

Salvar alterações deverá atualizar a tarefa existente, sem criar uma duplicata.

Cancelar a edição deverá descartar as modificações ainda não salvas.

RF-005 — Exclusão de tarefas

O sistema deverá solicitar confirmação antes de excluir uma tarefa.

A confirmação deverá identificar a tarefa que será excluída.

Se o usuário cancelar, nenhum dado deverá ser alterado.

Após a confirmação, a tarefa deverá ser removida da interface e do armazenamento.

RF-006 — Gerenciamento de status

O usuário poderá alterar o status de uma tarefa entre:

- Pendente.
- Em andamento.
- Concluída.

Uma tarefa concluída poderá voltar ao estado pendente ou em andamento.

As mudanças deverão atualizar os indicadores do dashboard e a visualização atual.

RF-007 — Pesquisa textual

O sistema deverá permitir pesquisar tarefas por título e descrição.

A pesquisa deverá:

- Ignorar diferenças entre letras maiúsculas e minúsculas.
- Remover espaços excedentes nas extremidades do termo pesquisado.
- Atualizar os resultados sem recarregar a página.
- Permitir limpar a pesquisa.
- Exibir uma mensagem quando não houver resultados.

RF-008 — Filtros combináveis

O usuário poderá filtrar simultaneamente por:

- Status.
- Prioridade.
- Categoria.
- Data de vencimento.
- Situação de atraso.

Os filtros deverão funcionar em conjunto usando a lógica AND: uma tarefa só aparecerá se satisfizer todos os filtros ativos.

Deverá existir uma ação para limpar todos os filtros.

RF-009 — Ordenação

O usuário poderá ordenar as tarefas por:

- Data de criação, mais recentes primeiro.
- Data de criação, mais antigas primeiro.
- Data de vencimento, mais próximas primeiro.
- Prioridade, da mais alta para a mais baixa.
- Ordem alfabética do título.

Tarefas sem data de vencimento deverão aparecer depois das tarefas com vencimento definido quando a ordenação for por vencimento.

A ordenação não deverá modificar os dados originais das tarefas.

RF-010 — Visualização em lista

O sistema deverá oferecer uma visualização em lista contendo, no mínimo:

- Título.
- Categoria.
- Prioridade.
- Status.
- Data de vencimento.
- Ações disponíveis.

A interface deverá diferenciar visualmente as tarefas concluídas e as atrasadas.

RF-011 — Visualização Kanban

O sistema deverá oferecer um quadro com três colunas:

1. Pendente.
2. Em andamento.
3. Concluída.

Cada tarefa deverá aparecer em uma única coluna, correspondente ao seu status atual.

Alterar o status no Kanban deverá atualizar os dados e o armazenamento.

Arrastar e soltar tarefas poderá ser implementado como funcionalidade adicional. Se implementado, deverá existir uma alternativa acessível por teclado ou controles convencionais.

RF-012 — Categorias

O sistema deverá oferecer categorias padrão, como:

- Estudos.
- Trabalho.
- Pessoal.
- Projetos.
- Outros.

O usuário poderá selecionar uma categoria durante o cadastro e a edição.

A arquitetura deverá permitir adicionar novas categorias sem modificar a lógica central das tarefas.

RF-013 — Tarefas atrasadas

Uma tarefa será considerada atrasada quando:

- Possuir uma data de vencimento anterior à data atual.
- Não estiver concluída.

A comparação deverá considerar a data local do usuário, sem produzir erros por diferenças de fuso horário.

Uma tarefa concluída não deverá ser contabilizada como atrasada, mesmo que sua data de vencimento tenha passado.

RF-014 — Persistência local

O sistema deverá utilizar localStorage para armazenar:

- Tarefas.
- Preferências de tema.
- Preferências persistentes de interface, quando aplicável.

A aplicação deverá carregar os dados salvos durante a inicialização.

Se o armazenamento estiver vazio, deverá apresentar um estado inicial apropriado.

Se os dados estiverem corrompidos ou em formato inválido, o sistema deverá tratar o erro sem encerrar toda a aplicação.

Nenhuma falha de leitura ou gravação deverá ser ocultada silenciosamente.

RF-015 — Exportação de dados

O usuário deverá poder exportar as tarefas em um arquivo JSON baixável.

O arquivo deverá conter uma versão do formato de dados e todas as informações necessárias para reconstruir as tarefas.

A exportação não deverá modificar os dados armazenados.

RF-016 — Importação de dados

O usuário poderá importar um arquivo JSON previamente exportado.

Antes de substituir ou mesclar dados, o sistema deverá:

- Validar a estrutura do arquivo.
- Validar os campos e tipos.
- Verificar os identificadores.
- Rejeitar arquivos inválidos.
- Apresentar uma prévia ou resumo da operação.
- Solicitar confirmação antes de modificar os dados atuais.

O sistema não deverá executar código contido no arquivo importado.

A importação deverá ser atômica: se a validação falhar, os dados anteriores deverão permanecer intactos.

RF-017 — Tema visual

O sistema deverá oferecer tema claro e escuro.

A escolha deverá permanecer após recarregar a página.

O contraste do texto e dos controles deverá continuar adequado nos dois temas.

RF-018 — Feedback ao usuário

A aplicação deverá apresentar feedback claro para:

- Cadastro bem-sucedido.
- Edição bem-sucedida.
- Exclusão confirmada.
- Importação e exportação.
- Falhas de armazenamento.
- Campos inválidos.
- Ausência de resultados.
- Ausência de tarefas cadastradas.

As mensagens não deverão depender exclusivamente de cores.

5. Regras de negócio

RN-001

O título de uma tarefa é obrigatório e não pode ser composto somente por espaços.

RN-002

Toda tarefa deverá possuir identificador único, status válido e prioridade válida.

RN-003

Uma tarefa concluída não poderá ser contabilizada como pendente, em andamento ou atrasada.

RN-004

Filtros, pesquisa e ordenação não poderão excluir ou alterar permanentemente tarefas.

RN-005

O dashboard deverá refletir o conjunto completo de tarefas, independentemente dos filtros aplicados à lista.

RN-006

A exclusão somente ocorrerá após confirmação explícita do usuário.

RN-007

Os dados importados deverão passar por validação antes de substituir ou mesclar o armazenamento atual.

RN-008

Datas de vencimento deverão utilizar um formato consistente, preferencialmente YYYY-MM-DD, para armazenamento de datas sem horário.

RN-009

A edição de uma tarefa deverá preservar seu identificador original e sua data de criação.

RN-010

A importação ou recuperação de dados não poderá permitir a execução de HTML ou JavaScript arbitrário por meio dos campos das tarefas.

6. Requisitos não funcionais

RNF-001 — Usabilidade

A interface deverá permitir que um usuário iniciante cadastre uma tarefa sem precisar consultar documentação externa.

RNF-002 — Responsividade

A aplicação deverá funcionar em larguras de tela a partir de 320 pixels, adaptando menus, formulários, listas e cartões.

RNF-003 — Acessibilidade

O sistema deverá:

- Utilizar HTML semântico.
- Associar rótulos aos campos.
- Permitir navegação por teclado.
- Apresentar foco visível.
- Oferecer nomes acessíveis aos botões com ícones.
- Comunicar erros junto aos respectivos campos.
- Utilizar contraste adequado.
- Respeitar a preferência por movimento reduzido.

RNF-004 — Desempenho

Para um conjunto de até 1.000 tarefas, operações comuns de pesquisa, filtragem e renderização deverão permanecer responsivas em um computador ou celular moderno.

Meta de teste: atualização visual em até 200 ms para operações comuns com esse volume, em ambiente de referência documentado.

RNF-005 — Compatibilidade

A aplicação deverá funcionar nas versões atuais dos principais navegadores modernos, incluindo Chrome, Firefox, Edge e Safari.

RNF-006 — Manutenibilidade

O código deverá ser organizado por responsabilidade, utilizar nomes claros e evitar duplicação desnecessária.

RNF-007 — Segurança

O sistema deverá tratar dados do usuário como conteúdo não confiável, evitando injeção de HTML e JavaScript.

A aplicação deverá evitar o uso de eval(), Function() e técnicas equivalentes para executar dados importados.

RNF-008 — Confiabilidade

Falhas de persistência, importação ou validação deverão produzir mensagens compreensíveis e preservar os dados sempre que tecnicamente possível.

RNF-009 — Privacidade

Os dados das tarefas deverão permanecer no navegador do usuário. Não deverá existir transmissão de dados a servidores externos.

RNF-010 — Testabilidade

As principais regras de negócio deverão ser separadas da manipulação visual, permitindo testes automatizados.

7. Modelo de dados

Cada tarefa deverá seguir uma estrutura equivalente a:

{
"id": "identificador-unico",
"title": "Estudar Matemática Discreta",
"description": "Resolver exercícios de funções",
"category": "Estudos",
"priority": "high",
"status": "pending",
"dueDate": "2026-10-20",
"createdAt": "2026-10-11T12:00:00.000Z",
"updatedAt": "2026-10-11T12:00:00.000Z"
}

Os valores internos permitidos para priority serão low, medium, high e urgent.

Os valores internos permitidos para status serão pending, in_progress e completed.

Os campos de data de vencimento poderão ser nulos quando não houver prazo.

Os exemplos de datas são ilustrativos. A aplicação deverá gerar datas reais no momento da operação.

O agente poderá propor ajustes ao modelo, desde que preserve todos os requisitos funcionais.

8. Arquitetura proposta

A aplicação deverá ser construída com separação lógica entre:

Camada de interface

Responsável por formulários, botões, cartões, tabelas, Kanban, feedback e navegação.

Camada de domínio

Responsável por validações, regras de negócio, filtros, ordenação, cálculos e transições de status.

Camada de persistência

Responsável por carregar e salvar tarefas e preferências no localStorage.

Camada de importação e exportação

Responsável por serialização, validação, prévia, confirmação e geração de arquivos JSON.

A implementação deverá evitar que regras de negócio importantes fiquem espalhadas pelos manipuladores de eventos da interface.

9. Estrutura de arquivos sugerida

taskflow/
├── index.html
├── css/
│   └── styles.css
├── js/
│   ├── app.js
│   ├── tasks.js
│   ├── storage.js
│   ├── filters.js
│   └── import-export.js
├── tests/
│   ├── tasks.test.js
│   ├── filters.test.js
│   └── storage.test.js
└── README.md

O agente poderá modificar essa estrutura quando houver justificativa técnica. A aplicação deverá continuar executável e testável.

10. Critérios de aceitação

CA-001

Dado que o usuário informe um título válido, quando salvar uma nova tarefa, então ela deverá aparecer na interface e permanecer disponível após recarregar a página.

CA-002

Dado que o título esteja vazio ou contenha apenas espaços, quando o usuário tentar salvar, então o sistema deverá rejeitar a operação e informar o erro.

CA-003

Dado que exista uma tarefa cadastrada, quando o usuário editar seu título e salvar, então o registro deverá ser atualizado sem criar outra tarefa.

CA-004

Dada uma tarefa existente, quando o usuário cancelar a confirmação de exclusão, então a tarefa deverá permanecer intacta.

CA-005

Dadas tarefas com diferentes status, quando o usuário filtrar por status e prioridade simultaneamente, então somente as tarefas que satisfaçam ambos os critérios deverão aparecer.

CA-006

Dada uma tarefa concluída cujo vencimento já passou, quando o dashboard calcular tarefas atrasadas, então ela não deverá ser contabilizada como atrasada.

CA-007

Dado que não existam tarefas, quando o dashboard for exibido, então os indicadores deverão apresentar zero e o percentual de conclusão não deverá produzir NaN ou Infinity.

CA-008

Dado um arquivo JSON inválido, quando o usuário tentar importá-lo, então o sistema deverá rejeitá-lo sem apagar ou substituir os dados atuais.

CA-009

Dada uma tarefa cujo título contenha texto semelhante a uma tag HTML, quando ela for exibida, então o conteúdo deverá aparecer como texto, sem executar marcação ou scripts.

CA-010

Dado que o usuário selecione o tema escuro, quando recarregar a página, então a preferência deverá ser mantida.

CA-011

Dado que o usuário utilize apenas o teclado, quando navegar pela aplicação, então deverá conseguir acessar os campos e controles essenciais, identificar o foco e concluir as operações principais.

CA-012

Dado um conjunto de 1.000 tarefas, quando pesquisar, filtrar ou ordenar, então a operação deverá atender à meta de desempenho definida no RNF-004, no ambiente de referência documentado.

11. Plano de testes

O agente deverá entregar testes automatizados e testes manuais documentados.

Testes funcionais

- Criar tarefa válida.
- Rejeitar título vazio.
- Rejeitar título excessivamente longo.
- Editar tarefa.
- Cancelar edição.
- Excluir tarefa.
- Cancelar exclusão.
- Alterar status.
- Reabrir tarefa concluída.
- Pesquisar por título.
- Pesquisar por descrição.
- Combinar filtros.
- Ordenar por prioridade.
- Ordenar por vencimento.
- Calcular percentual de conclusão.
- Identificar tarefas atrasadas.

Testes de persistência

- Carregar armazenamento vazio.
- Salvar e recuperar tarefas.
- Recuperar preferências de tema.
- Tratar JSON corrompido.
- Tratar indisponibilidade do localStorage.
- Confirmar que alterações permanecem após recarregar a página.

Testes de importação e exportação

- Exportar dados válidos.
- Importar arquivo válido.
- Rejeitar estrutura inválida.
- Rejeitar prioridade desconhecida.
- Rejeitar status desconhecido.
- Detectar identificadores duplicados.
- Cancelar importação sem alterar dados.
- Garantir que uma falha de validação não produza importação parcial.

Testes de segurança e interface

- Exibir conteúdo semelhante a HTML sem executá-lo.
- Testar navegação por teclado.
- Verificar mensagens de erro.
- Testar viewport de 320 px.
- Testar viewport de tablet.
- Testar viewport de desktop.
- Verificar contraste nos temas.
- Verificar ausência de erros inesperados no console.

12. Entregáveis obrigatórios

O agente deverá fornecer:

1. Código-fonte completo.
2. Todos os arquivos necessários para execução.
3. README com instruções de instalação e uso.
4. Explicação da arquitetura escolhida.
5. Mapeamento entre requisitos e funcionalidades implementadas.
6. Testes automatizados executáveis.
7. Resultados reais dos testes executados.
8. Lista de limitações conhecidas.
9. Lista de requisitos não implementados, se houver.
10. Instruções para reproduzir os testes manualmente.

Não será aceito um projeto composto apenas por protótipos visuais, botões sem comportamento, dados simulados ou funções vazias.

13. Definição de concluído

O projeto somente será considerado concluído quando:

- Todos os requisitos obrigatórios estiverem implementados ou explicitamente identificados como pendentes.
- Os fluxos principais funcionarem de ponta a ponta.
- Os dados persistirem corretamente.
- Os critérios de aceitação forem verificados.
- Os testes automatizados forem executados e seus resultados apresentados.
- A interface for utilizável em dispositivos móveis e por teclado.
- Não houver erros críticos conhecidos.
- A documentação permitir que outra pessoa execute e mantenha o projeto.

O agente deverá distinguir claramente funcionalidades implementadas, funcionalidades testadas e funcionalidades apenas planejadas.
