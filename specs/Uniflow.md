# SDD-UNIFLOW-001 — Sistema de Gestão Acadêmica

**Versão:** 1.0.0  
**Status:** Especificação para implementação  
**Tipo:** Aplicação web  
**Idioma:** Português brasileiro  
**Tecnologias:** HTML5, CSS3, JavaScript ES6+  
**Persistência inicial:** localStorage  
**Público-alvo:** Estudantes, professores e administradores  
**Objetivo do documento:** Definir os requisitos necessários para implementar, testar e validar o sistema.

## 1. Introdução

O UniFlow é um sistema web para gerenciamento de atividades acadêmicas. A aplicação deverá permitir o cadastro e gerenciamento de estudantes, disciplinas, avaliações, notas, frequência e relatórios acadêmicos.

O sistema deverá utilizar uma arquitetura modular, apresentar interface responsiva e manter a integridade dos dados.

A primeira versão será executada localmente, sem backend obrigatório. A autenticação apresentada em eventuais protótipos deverá ser identificada como demonstrativa, caso não exista servidor responsável pela segurança.

## 2. Objetivos

- Centralizar informações acadêmicas.
- Facilitar o gerenciamento de disciplinas e estudantes.
- Calcular médias automaticamente conforme regras configuráveis.
- Registrar frequência e faltas.
- Identificar estudantes em situação de risco acadêmico.
- Gerar relatórios e exportar informações.
- Garantir consistência dos dados entre as telas.
- Permitir testes automatizados e rastreabilidade dos requisitos.

## 3. Perfis de usuário

### 3.1 Administrador

Pode gerenciar estudantes, disciplinas, matrículas, avaliações e configurações acadêmicas.

### 3.2 Professor

Pode visualizar suas disciplinas, registrar avaliações, lançar notas e registrar frequência.

### 3.3 Estudante

Pode consultar suas próprias disciplinas, notas, frequência e situação acadêmica.

### 3.4 Modo local de demonstração

A implementação sem backend poderá disponibilizar dados fictícios e alternância de perfis para demonstração.

Essa funcionalidade não deverá ser apresentada como autenticação segura. Em produção, a autorização deverá ser aplicada no servidor.

## 4. Escopo funcional

O sistema deverá possuir os seguintes módulos:

1. Dashboard.
2. Gestão de estudantes.
3. Gestão de disciplinas.
4. Matrículas.
5. Avaliações e notas.
6. Frequência.
7. Relatórios.
8. Pesquisa e filtros.
9. Importação e exportação.
10. Configurações.

## 5. Requisitos funcionais

### RF-001 — Dashboard

Apresentar indicadores calculados a partir dos dados existentes:

- Total de estudantes cadastrados.
- Total de disciplinas.
- Total de matrículas ativas.
- Avaliações registradas.
- Estudantes abaixo da média.
- Estudantes com frequência abaixo do mínimo.
- Distribuição das médias por faixa.

Os indicadores deverão ser recalculados após alterações nos dados.

Não será permitido utilizar números fixos como substitutos dos dados reais.

### RF-002 — Cadastro de estudantes

Permitir cadastrar estudantes com:

- Identificador único.
- Nome completo.
- Matrícula institucional.
- E-mail.
- Curso.
- Período.
- Status acadêmico.
- Data de cadastro.

O nome deverá conter pelo menos dois caracteres após a remoção de espaços excedentes.

A matrícula deverá ser única.

O e-mail deverá passar por validação sintática básica.

O sistema deverá impedir registros duplicados de matrícula.

### RF-003 — Edição e exclusão de estudantes

Permitir editar informações de estudantes.

A edição deverá preservar o identificador original.

A exclusão deverá exigir confirmação.

Se o estudante possuir matrículas, notas ou frequência associadas, o sistema deverá impedir a exclusão destrutiva e orientar o usuário a inativar o registro ou executar um procedimento de arquivamento.

### RF-004 — Cadastro de disciplinas

Cada disciplina deverá possuir:

- Identificador único.
- Código institucional.
- Nome.
- Curso relacionado.
- Professor responsável.
- Carga horária.
- Período letivo.
- Média mínima para aprovação.
- Frequência mínima exigida.
- Status.

O código institucional deverá ser único.

A carga horária deverá ser positiva.

A média mínima deverá respeitar a escala de notas configurada.

A frequência mínima deverá ser um percentual entre 0 e 100.

### RF-005 — Matrículas

Permitir matricular estudantes em disciplinas.

O sistema deverá impedir matrículas duplicadas do mesmo estudante na mesma disciplina e período letivo.

Deverá ser possível consultar os estudantes matriculados em cada disciplina.

O sistema deverá impedir a associação de registros inexistentes.

### RF-006 — Avaliações

Permitir criar avaliações vinculadas a uma disciplina.

Cada avaliação deverá conter:

- Identificador único.
- Nome.
- Disciplina.
- Data.
- Peso.
- Nota máxima.
- Descrição opcional.

Os pesos deverão ser positivos.

Para disciplinas que utilizam média ponderada, a soma dos pesos das avaliações consideradas deverá ser maior que zero.

A edição ou exclusão de uma avaliação deverá atualizar os cálculos dependentes.

### RF-007 — Lançamento de notas

Permitir registrar notas para estudantes matriculados na disciplina correspondente.

Cada nota deverá pertencer a uma avaliação válida e a um estudante matriculado.

O valor deverá estar entre zero e a nota máxima definida para a avaliação.

Notas inexistentes não deverão ser interpretadas automaticamente como zero.

O sistema deverá distinguir:

- Nota não lançada.
- Nota igual a zero.
- Nota válida.
- Nota inválida.

### RF-008 — Cálculo de médias

O sistema deverá suportar dois modelos:

**Média aritmética:**

Média = soma das notas válidas / quantidade de notas válidas.

**Média ponderada:**

Média = soma de (nota normalizada × peso) / soma dos pesos considerados.

A normalização deverá converter as notas para a escala acadêmica configurada, quando as avaliações utilizarem notas máximas diferentes.

O sistema deverá permitir configurar quais avaliações entram no cálculo.

Avaliações sem nota não deverão ser consideradas como zero.

Quando não houver notas suficientes para calcular a média, a interface deverá apresentar "Média indisponível".

Os cálculos deverão utilizar precisão numérica consistente e arredondamento definido na especificação de cada disciplina.

### RF-009 — Situação acadêmica

O sistema deverá apresentar as seguintes situações:

- Aprovado.
- Reprovado por nota.
- Reprovado por frequência.
- Em andamento.
- Pendente de avaliação.

A situação deverá ser calculada conforme os critérios configurados.

Uma disciplina em andamento não deverá ser classificada como reprovação definitiva apenas porque ainda existem avaliações pendentes.

A interface deverá informar o motivo da situação apresentada.

### RF-010 — Frequência

Permitir registrar a frequência de estudantes matriculados.

Cada registro deverá conter:

- Estudante.
- Disciplina.
- Data da aula.
- Situação: presente, falta ou falta justificada.
- Observação opcional.

O sistema deverá impedir registros duplicados para o mesmo estudante, disciplina e sessão de aula.

A política de contabilização de faltas justificadas deverá ser configurável e documentada.

A frequência será calculada com base nas sessões registradas e na política configurada.

Quando não houver sessões registradas, o sistema deverá apresentar "Frequência indisponível".

### RF-011 — Alertas acadêmicos

Apresentar alertas para:

- Média inferior à mínima configurada.
- Frequência inferior ao mínimo.
- Avaliações pendentes.
- Notas inválidas.
- Matrículas inconsistentes.

Os alertas deverão ser derivados dos dados atuais e atualizados após alterações.

### RF-012 — Pesquisa e filtros

Permitir pesquisar estudantes por nome, matrícula ou e-mail.

Permitir filtrar por curso, período, status e disciplina.

Permitir pesquisar disciplinas por código e nome.

Os filtros simultâneos deverão funcionar com lógica AND.

Deverá existir uma opção para limpar os filtros.

### RF-013 — Relatórios

Permitir visualizar relatórios de:

- Notas por disciplina.
- Média por estudante.
- Frequência por estudante.
- Estudantes em risco acadêmico.
- Distribuição de médias.
- Matrículas por disciplina.

Os relatórios deverão refletir os dados existentes e informar os filtros aplicados.

### RF-014 — Exportação

Permitir exportar os dados em CSV e JSON.

Os arquivos deverão utilizar codificação UTF-8.

O CSV deverá tratar adequadamente separadores, aspas e quebras de linha.

A exportação deverá respeitar os filtros selecionados quando o usuário optar por exportar a visualização atual.

### RF-015 — Importação

Permitir importar arquivos JSON com estrutura documentada.

Antes da importação, o sistema deverá validar campos obrigatórios, tipos, identificadores, referências e restrições de unicidade.

O usuário deverá escolher entre substituir os dados e mesclar os registros, quando ambas as opções forem suportadas.

A operação deverá exigir confirmação.

A validação deverá ocorrer antes da gravação definitiva.

Uma importação inválida não poderá deixar o banco local parcialmente alterado.

### RF-016 — Persistência

Armazenar os dados no localStorage na versão inicial.

A aplicação deverá recuperar os dados após recarregar a página.

O sistema deverá lidar com dados corrompidos, indisponibilidade de armazenamento e limites de quota.

A interface deverá informar falhas de gravação.

Deverá existir uma estratégia documentada de exportação para cópia de segurança.

### RF-017 — Interface

Disponibilizar navegação lateral ou equivalente, cabeçalho, área de conteúdo e componentes consistentes.

A interface deverá incluir estados de carregamento quando necessários, estados vazios, mensagens de erro, confirmação de ações e notificações de sucesso.

### RF-018 — Responsividade e acessibilidade

A interface deverá funcionar em dispositivos móveis, tablets e computadores.

Os formulários deverão possuir rótulos acessíveis.

Os controles deverão funcionar por teclado.

O foco deverá ser visível.

O sistema deverá evitar depender exclusivamente de cores para comunicar estados.

### RF-019 — Configurações

Permitir configurar tema visual, escala de notas, arredondamento e parâmetros acadêmicos compatíveis com o escopo da aplicação.

Alterações nas configurações deverão ser validadas antes de serem aplicadas.

O sistema deverá informar quando uma configuração afetar cálculos existentes.

## 6. Regras de negócio

### RN-001
Todos os identificadores deverão ser únicos dentro de suas respectivas entidades.

### RN-002
Uma matrícula deverá referenciar um estudante e uma disciplina existentes.

### RN-003
Uma nota deverá referenciar uma avaliação válida e uma matrícula compatível.

### RN-004
Nenhuma nota poderá ser inferior a zero ou superior à nota máxima da avaliação.

### RN-005
Notas não lançadas deverão ser distintas de notas iguais a zero.

### RN-006
Os resultados acadêmicos deverão ser calculados a partir das regras configuradas, sem valores codificados arbitrariamente.

### RN-007
Alterações em avaliações deverão atualizar as médias dependentes.

### RN-008
Alterações em registros de frequência deverão atualizar os indicadores de frequência.

### RN-009
Registros referenciados por outros dados não poderão ser excluídos de maneira a gerar referências inválidas.

### RN-010
Operações canceladas não deverão alterar os dados.

### RN-011
Importações inválidas deverão preservar integralmente o estado anterior.

### RN-012
Dados apresentados em gráficos e indicadores deverão corresponder aos registros utilizados nos cálculos.

## 7. Modelo de dados

### Student

- id: string
- registrationNumber: string
- fullName: string
- email: string
- courseId: string
- period: integer
- status: active | inactive
- createdAt: ISO datetime

### Course

- id: string
- code: string
- name: string
- instructorId: string | null
- workloadHours: number
- term: string
- minimumGrade: number
- minimumAttendance: number
- gradingMethod: arithmetic | weighted
- status: active | inactive

### Enrollment

- id: string
- studentId: string
- courseId: string
- term: string
- status: active | completed | withdrawn

### Assessment

- id: string
- courseId: string
- name: string
- date: YYYY-MM-DD
- weight: number
- maximumGrade: number

### Grade

- id: string
- enrollmentId: string
- assessmentId: string
- value: number | null
- updatedAt: ISO datetime

### AttendanceSession

- id: string
- courseId: string
- date: YYYY-MM-DD
- description: string

### AttendanceRecord

- id: string
- sessionId: string
- enrollmentId: string
- status: present | absent | excused
- observation: string | null

As entidades deverão possuir referências consistentes. O sistema deverá validar a compatibilidade entre matrícula, disciplina, avaliação e registro de frequência.

## 8. Requisitos não funcionais

- RNF-001: código modular e legível.
- RNF-002: interface responsiva a partir de 320 px.
- RNF-003: navegação acessível por teclado.
- RNF-004: prevenção de injeção de HTML.
- RNF-005: ausência de dependências externas desnecessárias.
- RNF-006: testes automatizados para regras críticas.
- RNF-007: atualização consistente dos dados após operações.
- RNF-008: compatibilidade com navegadores modernos.
- RNF-009: operações de consulta responsivas para até 1.000 estudantes e 100 disciplinas no ambiente de referência.
- RNF-010: documentação de instalação, limitações e execução dos testes.
- RNF-011: nenhum envio de dados acadêmicos para servidores externos na versão local.
- RNF-012: resultados de testes apresentados com distinção entre testes executados e testes apenas planejados.

## 9. Arquitetura

A aplicação deverá separar as seguintes responsabilidades:

1. Interface: páginas, formulários, tabelas e componentes visuais.
2. Domínio: validações, regras acadêmicas, médias e frequência.
3. Repositórios: leitura e gravação de dados.
4. Relatórios: consultas e agregações.
5. Importação e exportação: serialização e validação.
6. Testes: validação isolada das regras de negócio.

O acesso ao armazenamento deverá ocorrer por uma camada própria, evitando chamadas dispersas ao localStorage em todos os componentes.

## 10. Critérios de aceitação

CA-001: o sistema rejeita matrículas duplicadas.

CA-002: uma nota acima da nota máxima é rejeitada.

CA-003: uma nota igual a zero é aceita.

CA-004: uma nota não lançada não é tratada como zero.

CA-005: médias são recalculadas após alterações nas avaliações.

CA-006: uma matrícula inválida não pode receber notas ou frequência.

CA-007: filtros combinados retornam somente os registros compatíveis.

CA-008: uma importação inválida não modifica os dados anteriores.

CA-009: relatórios refletem os dados reais e os filtros selecionados.

CA-010: indicadores do dashboard são atualizados após alterações.

CA-011: o sistema informa indisponibilidade de médias quando não existem notas suficientes.

CA-012: o sistema identifica corretamente registros de frequência inconsistentes.

CA-013: a interface permite navegação por teclado nos fluxos principais.

CA-014: os dados persistem após recarregar a aplicação.

CA-015: o sistema não executa conteúdo HTML ou JavaScript importado como texto de dados.

## 11. Plano de testes

### Testes unitários
- Validação de estudantes.
- Unicidade de matrícula.
- Cálculo de média aritmética.
- Cálculo de média ponderada.
- Normalização de notas.
- Arredondamento.
- Cálculo de frequência.
- Classificação de situação acadêmica.

### Testes de integração
- Cadastro de estudante e matrícula.
- Criação de avaliação e lançamento de nota.
- Alteração de nota e atualização de média.
- Registro de frequência e atualização de indicadores.
- Importação e exportação de dados.

### Testes negativos
- Matrícula duplicada.
- Nota negativa.
- Nota acima do limite.
- Avaliação inexistente.
- Referência de estudante inexistente.
- JSON corrompido.
- Falha de armazenamento.
- Importação com identificadores duplicados.

### Testes de interface
- Navegação por teclado.
- Layout móvel.
- Formulários inválidos.
- Mensagens de confirmação.
- Estados vazios.
- Atualização de indicadores.
- Exportação de arquivos.

## 12. Entregáveis

1. index.html funcional.
2. Arquivos CSS e JavaScript.
3. Dados de demonstração identificados como fictícios.
4. README.
5. Matriz de rastreabilidade.
6. Testes automatizados.
7. Evidências dos testes executados.
8. Relatório de limitações.
9. Instruções para execução local.

## 13. Definição de concluído

O sistema será considerado concluído quando os requisitos obrigatórios estiverem implementados ou formalmente identificados como pendentes, os critérios de aceitação tiverem sido verificados, os testes forem executados e a documentação permitir a reprodução do ambiente.

A declaração de conclusão deverá ser baseada em evidências, e não apenas na autoavaliação do agente.
