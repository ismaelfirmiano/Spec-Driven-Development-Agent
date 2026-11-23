# UNIFLOW 2.0
## Documento de Especificação e Projeto de Software (SDD)

### 1. Apresentação do projeto

Desenvolva uma aplicação web completa chamada UniFlow, destinada ao gerenciamento acadêmico de uma instituição de ensino.

O sistema deverá centralizar as informações de estudantes, professores, cursos, disciplinas, turmas, matrículas, avaliações, notas e frequência em uma única plataforma.

A aplicação deverá apresentar uma interface moderna, profissional, intuitiva e responsiva, permitindo que diferentes perfis de usuários realizem suas atividades acadêmicas de maneira organizada.

O projeto deverá ser desenvolvido inicialmente utilizando HTML5, CSS3 e JavaScript moderno, com persistência local dos dados por meio de localStorage.

A arquitetura deverá ser organizada de maneira que uma futura integração com backend e banco de dados seja possível sem a necessidade de reconstruir toda a aplicação.

### 2. Objetivo principal

O objetivo é desenvolver um sistema acadêmico que reproduza os principais processos administrativos e pedagógicos de uma instituição de ensino.

Não se trata apenas de criar uma página com formulários e tabelas. O sistema deverá possuir funcionalidades interligadas, regras de negócio consistentes, cálculos acadêmicos, validação de informações e atualização automática dos dados apresentados.

Todas as funcionalidades deverão operar com dados reais armazenados pela própria aplicação, utilizando dados fictícios apenas para demonstração inicial.

### 3. Interface e experiência do usuário

Ao acessar o sistema, o usuário deverá encontrar um painel administrativo com uma navegação lateral, cabeçalho, área principal de conteúdo e identificação do perfil selecionado.

A interface deverá apresentar identidade visual consistente, utilizando tipografia legível, espaçamento adequado, ícones coerentes e componentes reutilizáveis.

O usuário deverá conseguir navegar entre os módulos sem precisar recarregar a página inteira.

O sistema deverá possuir tema claro e escuro, com preferência armazenada localmente.

Em dispositivos móveis, a navegação deverá se adaptar à largura da tela, substituindo menus laterais extensos por uma navegação compacta.

Todas as páginas deverão apresentar estados visuais apropriados para carregamento, ausência de dados, erros e operações concluídas.

### 4. Painel principal

O dashboard deverá apresentar uma visão geral da instituição.

Na parte superior, deverão aparecer cartões com a quantidade de estudantes ativos, professores, cursos, disciplinas, turmas e matrículas.

Também deverão ser apresentados indicadores de desempenho acadêmico, incluindo média geral, frequência média e percentual de aprovação.

O usuário deverá poder selecionar um período letivo e filtrar os indicadores por curso ou turma.

Abaixo dos indicadores, deverão existir gráficos mostrando a evolução das matrículas, a distribuição das notas, o desempenho das disciplinas e a frequência dos estudantes.

Os gráficos deverão ser construídos a partir dos registros existentes. Não deverão apresentar números fictícios como se fossem resultados reais.

O dashboard deverá ser atualizado automaticamente quando houver alterações nos dados acadêmicos.

### 5. Gerenciamento de estudantes

O sistema deverá possuir uma área dedicada ao gerenciamento de estudantes.

O usuário deverá conseguir cadastrar um estudante informando nome completo, matrícula institucional, e-mail, curso, período e situação acadêmica.

A matrícula deverá ser única. Não poderá existir mais de um estudante com o mesmo identificador institucional.

O formulário deverá validar os campos obrigatórios e apresentar mensagens claras quando houver informações inválidas.

Na listagem de estudantes, deverá ser possível pesquisar por nome, matrícula e e-mail, além de filtrar os registros por curso, período e situação.

Cada estudante deverá possuir uma página de detalhes com suas informações pessoais, histórico de matrículas, disciplinas cursadas, notas, frequência e resultados acadêmicos.

O sistema deverá permitir editar e inativar estudantes. A inativação não poderá apagar o histórico acadêmico.

Caso existam registros relacionados ao estudante, a exclusão definitiva deverá ser bloqueada para evitar perda de informações e referências inválidas.

### 6. Gerenciamento de professores

O sistema deverá permitir cadastrar e administrar professores.

Cada professor deverá possuir nome, e-mail, especialidade e situação.

Será possível associar professores às disciplinas e turmas correspondentes.

O usuário deverá conseguir visualizar as turmas atribuídas a cada professor e consultar sua carga horária.

Um professor inativo não poderá receber novas atribuições.

A substituição de um professor não deverá modificar o histórico de avaliações ou registros acadêmicos anteriores.

### 7. Gerenciamento de cursos e disciplinas

O sistema deverá permitir cadastrar cursos, definindo nome, código, modalidade, carga horária total, quantidade de períodos e situação.

Cada curso deverá possuir uma matriz curricular contendo suas disciplinas.

As disciplinas deverão possuir código, nome, carga horária, ementa, créditos, média mínima, frequência mínima e critérios de avaliação.

Também deverá ser possível estabelecer pré-requisitos entre disciplinas.

Antes de permitir uma matrícula, o sistema deverá verificar se o estudante cumpriu os pré-requisitos necessários.

A aplicação deverá impedir dependências circulares entre disciplinas.

### 8. Gerenciamento de turmas

O sistema deverá permitir criar turmas associadas a disciplinas e períodos letivos.

Cada turma deverá possuir professor responsável, capacidade máxima, horários, período e situação.

As situações possíveis deverão incluir planejada, aberta, em andamento, encerrada e cancelada.

O sistema deverá impedir novas matrículas em turmas encerradas ou canceladas.

Também deverá impedir que a quantidade de estudantes ultrapasse a capacidade máxima.

O usuário deverá conseguir consultar os estudantes matriculados em cada turma.

### 9. Sistema de matrículas

O módulo de matrículas deverá conectar estudantes às turmas disponíveis.

Ao realizar uma matrícula, o sistema deverá verificar se o estudante está ativo, se a turma aceita novas matrículas, se existe capacidade disponível e se os pré-requisitos foram cumpridos.

Não deverá ser permitido cadastrar duas matrículas equivalentes para o mesmo estudante, turma e período letivo.

O sistema deverá permitir cancelar ou trancar matrículas, preservando o histórico da operação.

A situação da matrícula deverá ser refletida nos módulos de notas, frequência e relatórios.

### 10. Avaliações e lançamento de notas

O sistema deverá permitir que professores registrem diferentes tipos de avaliação, como provas, trabalhos, projetos, seminários e atividades.

Cada avaliação deverá possuir nome, data, peso, nota máxima e descrição.

O professor deverá conseguir consultar os estudantes matriculados na turma e lançar suas respectivas notas.

O sistema deverá validar se a nota está dentro dos limites permitidos.

Uma nota não lançada deverá ser tratada de maneira diferente de uma nota igual a zero.

Quando uma avaliação for alterada, os cálculos acadêmicos relacionados deverão ser atualizados.

Alterações em notas já registradas deverão ser identificadas no histórico de auditoria.

### 11. Motor de cálculo acadêmico

O sistema deverá possuir um módulo independente responsável pelos cálculos das médias.

Deverá permitir média aritmética, média ponderada, avaliação por etapas e recuperação final.

No modelo ponderado, o cálculo deverá considerar a nota normalizada de cada avaliação e seu respectivo peso.

Quando as avaliações possuírem notas máximas diferentes, o sistema deverá normalizar os resultados antes de calcular a média.

A recuperação deverá seguir uma política configurável para cada disciplina.

O sistema não deverá assumir que todas as instituições utilizam a mesma fórmula de aprovação.

Quando não houver avaliações suficientes, deverá informar que a média ainda não está disponível.

A situação acadêmica deverá ser apresentada como aprovado, reprovado por nota, reprovado por frequência, em recuperação, em andamento ou pendente de avaliação.

O sistema deverá informar o motivo da classificação apresentada.

### 12. Controle de frequência

O módulo de frequência deverá permitir registrar sessões de aula e controlar a presença dos estudantes.

O professor deverá selecionar uma turma, uma data e uma sessão para registrar os estudantes presentes, ausentes ou com falta justificada.

Não deverá ser permitido registrar duas presenças para o mesmo estudante na mesma sessão.

O sistema deverá calcular o total de presenças, faltas e percentual de frequência.

A contabilização das faltas justificadas deverá seguir uma configuração institucional.

O histórico de frequência deverá estar disponível na página de detalhes do estudante e nos relatórios da disciplina.

### 13. Calendário acadêmico

A aplicação deverá possuir um calendário acadêmico com eventos relacionados às atividades da instituição.

Deverão aparecer datas de avaliações, períodos letivos, aulas, prazos, eventos e feriados cadastrados.

O usuário deverá conseguir navegar entre meses e consultar os detalhes de cada evento.

Também deverá ser possível filtrar os eventos por curso, disciplina e turma.

### 14. Alertas acadêmicos

O sistema deverá identificar situações que merecem atenção.

Entre elas estão estudantes com média inferior ao mínimo, frequência insuficiente, avaliações pendentes, matrículas irregulares e turmas próximas da capacidade máxima.

Os alertas deverão possuir descrição, data, categoria e nível de severidade.

O usuário poderá marcar alertas como lidos.

Os alertas deverão ser gerados a partir das informações armazenadas e não de mensagens predefinidas sem relação com os dados reais.

### 15. Relatórios

O sistema deverá possuir um módulo de relatórios com filtros por período, curso, disciplina, turma e situação acadêmica.

Deverá permitir gerar relatórios de desempenho individual, desempenho por turma, frequência, aprovação, reprovação, matrículas e distribuição de notas.

Os resultados deverão ser apresentados em tabelas e gráficos.

O usuário deverá poder exportar os relatórios para CSV e JSON.

Os arquivos exportados deverão preservar corretamente caracteres especiais da língua portuguesa.

O relatório deverá identificar os filtros utilizados e o período analisado.

### 16. Auditoria e histórico

O sistema deverá manter um histórico das principais operações realizadas.

Deverão ser registrados cadastros, edições, alterações de notas, registros de frequência, matrículas, cancelamentos, importações e mudanças nas configurações.

Cada registro deverá identificar a operação, o elemento alterado, a data e o resumo da mudança.

Na versão local, o histórico será apenas demonstrativo e não deverá ser apresentado como mecanismo inviolável de segurança.

O usuário deverá conseguir consultar o histórico, mas não editar os registros diretamente pela interface.

### 17. Importação e exportação

A aplicação deverá permitir exportar os dados em arquivos JSON e CSV.

Também deverá permitir importar arquivos previamente exportados.

Antes de concluir uma importação, o sistema deverá verificar se o arquivo possui estrutura válida, identificadores únicos, campos obrigatórios e referências existentes.

O usuário deverá visualizar um resumo da operação e confirmar a importação.

Caso o arquivo apresente inconsistências, a operação deverá ser cancelada sem modificar os dados existentes.

A aplicação deverá oferecer opções de substituição ou mesclagem quando tecnicamente suportadas, explicando as consequências de cada operação.

### 18. Segurança e integridade

Todos os dados recebidos deverão ser tratados como conteúdo não confiável.

O sistema deverá impedir que textos inseridos nos formulários sejam interpretados como código HTML ou JavaScript.

As validações deverão ocorrer na camada responsável pelas regras de negócio, e não somente na interface.

A aplicação deverá impedir referências inexistentes, matrículas duplicadas, notas fora dos limites e registros inconsistentes.

Falhas de armazenamento deverão ser apresentadas ao usuário, sem ocultar erros importantes.

Como a primeira versão utiliza armazenamento local, o sistema não deverá afirmar que possui autenticação institucional ou segurança equivalente a uma aplicação com backend.

### 19. Organização técnica

O projeto deverá ser organizado em módulos separados para interface, regras de negócio, serviços, persistência e relatórios.

A lógica dos cálculos acadêmicos deverá ser independente dos componentes HTML.

As funções de validação deverão ser reutilizáveis.

O sistema deverá utilizar nomes claros para arquivos, funções e variáveis.

Não deverão existir funções vazias, botões sem comportamento ou dados estáticos utilizados como substitutos de funcionalidades solicitadas.

A implementação deverá ser preparada para manutenção e expansão.

### 20. Testes e validação

O agente deverá testar o cadastro de estudantes, a criação de disciplinas, as matrículas, o lançamento de notas e os registros de frequência.

Também deverá testar situações inválidas, como matrículas duplicadas, notas acima do limite, estudantes inexistentes, avaliações inválidas e importações corrompidas.

Deverá verificar se as médias são recalculadas corretamente após alterações nas avaliações.

Deverá verificar se os relatórios apresentam os mesmos resultados dos registros utilizados nos cálculos.

A aplicação deverá ser testada em diferentes tamanhos de tela e por navegação com teclado.

Os testes automatizados deverão ser executados e seus resultados apresentados.

O agente não poderá afirmar que um teste foi aprovado sem apresentar evidências de sua execução.

### 21. Entrega final

O resultado deverá ser uma aplicação web funcional, com todos os arquivos necessários para execução.

Deverá incluir o código HTML, CSS e JavaScript, os dados de demonstração, a documentação de instalação, a descrição da arquitetura e os testes automatizados.

O agente também deverá apresentar uma análise comparando as funcionalidades implementadas com as exigências deste documento.

Deverá identificar claramente qualquer requisito não implementado, limitação técnica ou problema encontrado.

O projeto somente será considerado concluído quando as funcionalidades principais estiverem operacionais, os dados estiverem consistentes, os testes críticos tiverem sido executados e a documentação estiver disponível.