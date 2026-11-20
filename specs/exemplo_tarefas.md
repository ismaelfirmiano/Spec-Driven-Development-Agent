# UNIFLOW 2.0 — SDD (AGENT SPEC)
**Versão:** 2.0.1 | **Stack:** HTML5, CSS3, JS ES6+ (Vanilla, sem dependências externas obrigatórias) | **Persistência:** `localStorage` via Repositories (preparado para futura troca por API REST/SQL) | **Idioma:** pt-BR.

## 1. ESCOPO E ARQUITETURA
Sistema web local de gestão acadêmica. Funcionalidades externas (auth real, e-mail, pagamentos, nuvem) estão fora do escopo; se exibidas, rotular explicitamente como `[SIMULADO]`. Dados fictícios de seed devem ser rotulados como `[DEMO]`.

### Camadas (Strict Separation of Concerns)
1. **Apresentação (`css/`, `js/modules/`):** UI, eventos DOM, gráficos, modais. **Proibido:** lógica de negócio ou cálculos acadêmicos.
2. **Aplicação (`js/application/`):** Casos de uso, orquestração de fluxos, transações.
3. **Domínio (`js/domain/`):** Entidades, máquinas de estado, cálculos, regras de validação.
4. **Infraestrutura (`js/infrastructure/`):** `localStorage` adapter, repositórios, auditoria, import/export.
5. **Core (`js/core/`):** Router/navegação, state store, event bus, sanitização e validadores base.

*Estrutura base:* `index.html`, `manifest.json`, `README.md`, `css/`, `js/{core,domain,application,infrastructure,modules}/`, `tests/`, `docs/`. (Adaptações permitidas mediante justificativa técnica no README).

## 2. MODELO DE DADOS E RELAÇÕES
Validar integridade referencial e unicidade de IDs antes de qualquer persistência:
- **Instituição:** `{ id, nome, config: { periodoAtual, escalaNotas, arredondamento, freqMinima, criteriosAprovacao, tema } }`
- **Estudante:** `{ id, matricula, nome, email, cursoId, status: 'ativo'|'inativo' }`
- **Professor:** `{ id, nome, email, especialidade, status: 'ativo'|'inativo' }`
- **Curso:** `{ id, codigo, nome, modalidade: 'presencial'|'semipresencial'|'EAD', cargaHoraria, periodos, coordenador, matrizCurricular[] }`
- **Disciplina:** `{ id, codigo, nome, cursoId, cargaHoraria, ementa, creditos, preRequisitosIds[], mediaMinima, freqMinima, politicaAvaliacao }`
- **Turma:** `{ id, disciplinaId, professorId, periodo, capacidadeMax, horarios, status: 'planejada'|'aberta'|'em_andamento'|'encerrada'|'cancelada' }`
- **Matrícula:** `{ id, estudanteId, turmaId, status: 'ativa'|'trancada'|'cancelada'|'concluida', dataCriacao }`
- **Avaliação:** `{ id, turmaId, tipo, nome, peso, notaMax, data, prazo, criterios, encerrada: bool }`
- **Nota:** `{ id, matriculaId, avaliacaoId, valor: number|null, dataAtualizacao }` *(Diferenciar `null` [pendente] de `0`)*
- **SessãoFrequência:** `{ id, turmaId, data, descricao }`
- **RegistroFrequência:** `{ id, sessaoId, matriculaId, status: 'presente'|'falta'|'justificada' }`
- **Alerta:** `{ id, tipo, severidade, entidadeRef, descricao, data, lido: bool }`
- **Auditoria:** `{ id, operacao, entidade, registroId, timestamp, diffResumo, ator }` *(Append-only na UI)*

## 3. REGRAS DE NEGÓCIO POR MÓDULO
- **3.1 Dashboard:** KPIs em tempo real (ativos, turmas abertas, média geral, frequência média, taxa aprovação, alunos em risco). Gráficos (evolução matrículas, distribuição notas, freq/curso, aprovação/período, desempenho/disciplina) com alternativas textuais e filtros (período, curso, turma).
- **3.2 Estudantes:** CRUD + inativar/reativar (nunca deletar histórico). Perfil individual com histórico completo, pendências e exportação individual.
- **3.3 Professores:** CRUD + especialidade e alocação. Bloquear novas turmas se `inativo`. Edição não altera histórico de avaliações passadas.
- **3.4 Cursos & 3.5 Disciplinas:** CRUD. Validar DAG na matriz curricular (bloquear pré-requisitos circulares).
- **3.6 Turmas & 3.7 Matrículas:** Bloquear matrícula se: estudante inativo, turma != `aberta`, `vagas <= 0`, matrícula duplicada, pré-requisitos pendentes ou período incompatível. Trancar/cancelar preserva histórico.
- **3.8 Avaliações & 3.9 Cálculos (Módulo Isolado):** Suportar média aritmética, ponderada (`Σ((nota / notaMax) * peso) / Σ(pesos)`), por etapas e recuperação (fórmula configurável por disciplina). Respeitar arredondamento configurado. Status resultantes: `aprovado`, `reprovado_nota`, `reprovado_freq`, `em_recuperacao`, `em_andamento`, `pendente`. Alterar nota/avaliação encerrada dispara recálculo e auditoria.
- **3.10 Frequência:** CRUD de sessões e chamadas. Bloquear registro duplicado (mesmo aluno/sessão). Contabilização de `falta_justificada` configurável.
- **3.11 Calendário:** Exibir períodos, aulas, avaliações, prazos, eventos e feriados. Filtros por curso/disciplina/turma. Diferenciação visual + textual (acessibilidade).
- **3.12 Alertas:** Geração determinística baseada em regras (baixa freq, média insuficiente, nota pendente, matrícula irregular, pré-requisito, lotação turma, inconsistência). Proibido alertas sem condição verificável.
- **3.13 Relatórios:** Estudantes, professores, matrículas, frequência, desempenho, aprovação, evasão simulada e ocupação. Filtros, ordenação, exportação e cabeçalho com metadados dos filtros aplicados.
- **3.14 Auditoria:** Log automático para CUD, notas, frequência, matrículas, imports e configs. Somente leitura na UI (explicitar limitação local).
- **3.15 Import/Export:** Backup completo JSON e CSVs (estudantes, matrículas, notas, frequência). Pipeline obrigatório de importação: `Parse -> Validar Schema/Tipos/IDs/Refs/Regras -> Preview com erros -> Confirmação -> Gravação Atômica` (nunca gravação parcial).
- **3.16 Configurações:** Alterações que impactam cálculos exigem modal de confirmação explicando impacto + recálculo global + log de auditoria.

## 4. REQUISITOS NÃO-FUNCIONAIS E SEGURANÇA
- **XSS & Sanitização:** **PROIBIDO** usar `innerHTML` com dados dinâmicos/usuário. Usar `textContent` ou DOM APIs seguras. Tratar dados importados como não confiáveis.
- **Resiliência & Performance:** Versionar schema no `localStorage`; tratar JSON corrompido sem perda silenciosa (oferecer recovery/reset). Suportar fluentemente ~1.000 estudantes, 100 disciplinas e 5.000 registros.
- **UI/A11y:** Responsivo a partir de `320px`, HTML semântico, navegação completa por teclado com `:focus-visible`, suporte a Dark Mode. Sem botões decorativos (toda ação funciona ou tem tag `[SIMULADO]`).

## 5. TESTES E CRITÉRIOS DE ACEITAÇÃO
Executar suíte automatizada real em `tests/` e anexar evidências de execução:
1. **Unitários:** Cálculos (aritmética, ponderada, normalização, recuperação, arredondamento), frequência, detector de ciclo em pré-requisitos, vagas e transições de estado.
2. **Integração:** Fluxo completo matrícula -> avaliação -> nota -> recálculo -> alerta; importação atômica; mudança de config -> recálculo.
3. **Segurança:** Injeção HTML/XSS, JSON malformado, IDs duplicados, refs órfãs, notas fora do range, storage corrompido.
4. **UI:** Viewports (320px, 768px, 1280px), teclado, temas, filtros e exports.

### Checklist de Entrega Final do Agente
- [ ] Código-fonte modular + dados `[DEMO]` + `README.md` + `docs/` (contrato API, dicionário de dados, matriz de rastreabilidade).
- [ ] Evidências reais da execução dos testes (não afirmar conclusão sem output de teste).
- [ ] Relatório final separando explicitamente: **Implementado e Testado**, **Pendente** e **Limitações Conhecidas**.