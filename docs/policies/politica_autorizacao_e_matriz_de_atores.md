# Politica de Autorizacao e Governanca de Acesso

## 1. Objetivo
Estabelecer as diretrizes de controle de acesso para a plataforma, garantindo o **Principio do Menor Privilegio**. Esta politica define a **relacao tridimensional** entre **Atores** (papeis humanos e principals tecnicos), **Casos de Uso** (`Capabilities`) e os limites de seus **Escopos** (`Tenants`/`Courses`), servindo como **especificacao executavel** para engenharia e testes. O sistema adota um modelo hibrido de autorizacao baseado em papeis (**RBAC**) com validacao de escopos e atributos (**ABAC**).

---

## 2. Taxonomia de Atores

### Nivel 0: Plataforma (Cross-Tenant)
* **`administrador_plataforma`** - Superusuario do SaaS. Nao possui `Membership`. Identificado pelo sinalizador `is_superuser` no mecanismo de autenticacao. Escopo global, irrestrito entre tenants. Responsavel pela saude do software, criacao de instituicoes e gestao de recursos globais.

### Nivel 1: Estrategico Institucional
* **`direcao_estrategica`** - `Membership` com `course_id = null`. Autoridade de governanca institucional: configuracao do tenant, concessao e revogacao de papeis, gestao de identidade e vinculos. Inclui diretor geral e cargos equivalentes.
* **`gestao_financeira`** - `Membership` com `course_id = null`. Autoridade sobre saude financeira da instituicao. Unico papel que pode suspender `Membership` por inadimplencia e reativa-lo apos confirmacao de pagamento. Inclui controller financeiro e cargos equivalentes. *(escopo financeiro completo previsto para Fase 2)*

### Nivel 2: Operacional Interno
* **`secretaria`** - Guardiao do vinculo legal e contratual (`Enrollment`/`Membership`). Atua no ciclo de vida de entrada e saida do usuario no ecossistema: matriculas, transferencias e emissao de documentos oficiais. Escopo institucional ou por curso.
* **`coordenacao`** - Guardiao da qualidade de ensino e conformidade curricular. Foco em conteudo (`Course`/`Subject`) e desempenho (`Grades`/`Calendar`). Responsavel por fechamento de periodos, aprovacao de diarios e alocacao docente. Escopo institucional ou por curso.
* **`suporte_adm`** - Operador administrativo com escopos restritos e permissoes pontuais delegadas pela `direcao_estrategica`.

### Nivel 3: Execucao Curricular
* **`professor`** - Escopo sempre restrito ao `course_id` das proprias atribuicoes ativas de componentes curriculares.

### Nivel 4: Utilizador Final
* **`estudante`** - Acesso estritamente pessoal (self-service) aos proprios registros academicos e financeiros.
* **`responsavel`** - Acesso limitado aos dados dos estudantes vinculados via `guardian_id`.

### Automatos e Servicos
* **`sistema`** - Jobs agendados e rotinas de consolidacao de dados. Deve registrar ID da rotina e timestamp em toda acao.
* **`integracao_autorizada`** - APIs de terceiros e sistemas parceiros com credenciais dedicadas.

---

## 3. Modelo de Dados de Autorizacao (ERD Conceitual)

### Relacionamentos principais

```text
+--------------+            +-------------------+            +-----------------+
|     User     | 1        N |    Membership     | N        1 |   Institution   |
| (Identity)   +------------+ (Tenant Boundary) +------------+    (Tenant)     |
+--------------+            +---------+---------+            +-----------------+
                                      | N
                                      |
                                      | 1
                            +---------+---------+
                            |       Role        |
                            | (Policy Catalog)  |
                            +---------+---------+
                                      |
                                      | capabilities
                                      | (mapa estatico no Dominio - nao persistido em banco)
                                      |
                            +---------+---------+
                            |    Capability     |
                            | (StrEnum no       |
                            |   Dominio)        |
                            +-------------------+
```

- Um `User` pode ter multiplos `Membership` (um por instituicao/curso)
- Uma `Institution` pode ter multiplos `Membership` (um por usuario/curso)
- Um `Role` define o conjunto de `Capabilities` que o `Membership` herda
- `Capabilities` sao um mapa estatico no dominio (`frozenset[Capability]` computado a partir de `Role.code`) e nao sao armazenadas em banco de dados
- O `Membership` referencia `Role` pelo `role_id` e nao carrega escopos diretamente

### Edge Cases documentados

**Administrador da Plataforma**
Nao possui `Membership`. Identificado pelo sinalizador `is_superuser` no mecanismo de autenticacao (Django auth). A camada de autorizacao verifica esse sinalizador antes de exigir `Membership`, concedendo acesso global irrestrito.

**Aluno Menor de Idade**
O campo `guardian_id` pertence ao aggregate `User` (identidade), nao ao `Membership` (vinculo). O responsavel legal e o mesmo independente da escola em que o aluno estiver matriculado.

**Troca de Escola**
Quando um aluno muda de instituicao, o `Membership` anterior transiciona para `INACTIVE` e um novo `Membership` e criado na nova instituicao. O historico do vinculo anterior e preservado nativamente. Nenhum dado e apagado.

**Suspensao por Inadimplencia (`gestao_financeira`)**
A `gestao_financeira` suspende o `Membership.state` (vinculo institucional), nunca o `User.state` (identidade global). Se o mesmo aluno estiver matriculado na Escola A e na Escola B, a inadimplencia na Escola A suspende apenas o `Membership` da Escola A - o acesso a Escola B permanece intacto. O `User` continua `ACTIVE`. Isso garante que a identidade global nao seja penalizada por conflitos financeiros de um tenant especifico.

---

## 4. Matriz de Autorizacao Operacional
A autorizacao e validada na camada de **Application**, antes da execucao de qualquer logica de dominio.

Esta secao e normatizada pelo [ADR 034 - Matriz Operacional de Autorizacao com Capabilities Explicitas](../adr/30-identity-access/034-operational-authorization-matrix-and-capabilities.md).

Observacoes:
- a coluna `Capability requerida` usa o nome do enum por legibilidade; o valor serializado canonico continua no formato `resource:action`
- principals tecnicos (`sistema`, `integracao_autorizada`, `administrador_plataforma`) podem satisfazer a capability por contrato proprio, sem instanciar `Role`
- linhas marcadas como `(futuro)` documentam extensao esperada, mas nao entram no minimo obrigatorio de implementacao ate que o caso de uso seja promovido

| Caso de Uso | Ator | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cadastrar Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao (cross-tenant) | N/A | `USER_CREATE` |
| **Cadastrar Usuario** | `direcao_estrategica` | Equipe da instituicao | `target_membership.institution_id == actor.institution_id` | Fluxo composto de onboarding institucional | `USER_CREATE` + `MEMBERSHIP_CREATE` |
| **Cadastrar Usuario** | `secretaria` | Alunos e responsaveis | `target_membership.institution_id == actor.institution_id` | `target.role` deve ter nivel inferior ao da secretaria; `User` e `Membership` devem nascer na mesma transacao | `USER_CREATE` + `MEMBERSHIP_CREATE` |
| **Cadastrar Usuario** | `sistema` | Alunos | Baseado no contrato do gateway de pagamento | Fluxo tecnico auditavel | `USER_CREATE` + `MEMBERSHIP_CREATE` |
| **Ativar Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao | `User.state == PENDING` | `USER_ACTIVATE` |
| **Ativar Usuario** | `direcao_estrategica` | Usuarios do proprio tenant | `target_membership.institution_id == actor.institution_id` | `User.state == PENDING` | `USER_ACTIVATE` |
| **Desbloquear Usuario** | `direcao_estrategica` | Usuarios do proprio tenant | `target_membership.institution_id == actor.institution_id` | `User.state == SUSPENDED` | `USER_UNLOCK` |
| **Desbloquear Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao | `User.state == SUSPENDED`; intervencao de emergencia; audit trail obrigatorio | `USER_UNLOCK` |
| **Desbloquear Usuario** | `suporte_adm` | Usuarios do proprio tenant | `target_membership.institution_id == actor.institution_id` | `User.state == SUSPENDED`; requer autorizacao explicita | `USER_UNLOCK` |
| **Suspender Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao | `User.state == ACTIVE`; requer justificativa; audit trail obrigatorio | `USER_SUSPEND` |
| **Encerrar Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao | `User.state in (ACTIVE, SUSPENDED)`; irreversivel; requer justificativa | `USER_CLOSE` |
| **Vincular Usuario a Instituicao** | `administrador_plataforma` | Qualquer vinculo | Sem restricao | `User.state == ACTIVE` | `MEMBERSHIP_CREATE` |
| **Vincular Usuario a Instituicao** | `direcao_estrategica` | Vinculos do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == ACTIVE` | `MEMBERSHIP_CREATE` |
| **Ativar Membership** | `administrador_plataforma` | Qualquer `Membership` | Sem restricao | `Membership.state == SUSPENDED` | `MEMBERSHIP_ACTIVATE` |
| **Ativar Membership** | `direcao_estrategica` | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == SUSPENDED` | `MEMBERSHIP_ACTIVATE` |
| **Ativar Membership** | `gestao_financeira` | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == SUSPENDED`; reativacao apos confirmacao de pagamento | `MEMBERSHIP_ACTIVATE` |
| **Suspender Membership** | `direcao_estrategica` | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == ACTIVE`; requer justificativa | `MEMBERSHIP_SUSPEND` |
| **Suspender Membership** | `gestao_financeira` | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == ACTIVE`; inadimplencia; requer justificativa | `MEMBERSHIP_SUSPEND` |
| **Encerrar Membership** | `administrador_plataforma` | Qualquer `Membership` | Sem restricao | `Membership.state in (ACTIVE, SUSPENDED)`; irreversivel; requer justificativa | `MEMBERSHIP_CLOSE` |
| **Encerrar Membership** | `direcao_estrategica` | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state in (ACTIVE, SUSPENDED)`; irreversivel; requer justificativa | `MEMBERSHIP_CLOSE` |
| **Cadastrar Instituicao** *(organizacional)* | `administrador_plataforma` | Nova `Institution` | Sem restricao (cross-tenant) | Cria o tenant; dados minimos obrigatorios | `INSTITUTION_CREATE` |
| **Configurar Instituicao** *(organizacional)* | `direcao_estrategica` | Propria `Institution` | `target.institution_id == actor.institution_id` | Perfil, endereco, contato, logo | `INSTITUTION_CONFIGURE` |
| **Configurar Instituicao** *(organizacional)* | `secretaria`, `suporte_adm` | Propria `Institution` | `target.institution_id == actor.institution_id` | Delegado pela `direcao_estrategica` | `INSTITUTION_CONFIGURE` |
| **Cadastrar Rede, Instituicao e Unidade** | `administrador_plataforma` | Estrutura organizacional global | Sem restricao (cross-tenant) | Duplicidade organizacional resolvida; politica de cadastro organizacional aplicada | `NETWORK_STRUCTURE_CREATE` |
| **Criar Matricula** | `secretaria`, `sistema`, `integracao_autorizada` | Alunos do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == ACTIVE`, `Membership.state == ACTIVE` | `ENROLLMENT_CREATE` |
| **Consultar Matricula** | `secretaria`, `coordenacao`, `suporte_adm`, `sistema` | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | N/A | `ENROLLMENT_READ` |
| **Listar Historico de Matricula** | `secretaria`, `coordenacao`, `suporte_adm`, `sistema` | Historico append-only da matricula | `target.institution_id == actor.institution_id` | Acesso a trilha de auditoria permitido | `ENROLLMENT_HISTORY_READ` |
| **Suspender Matricula** | `secretaria`, `sistema` | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | `Enrollment.state == ACTIVE`; exige justificativa; politicas externas permitem suspensao | `ENROLLMENT_SUSPEND` |
| **Reativar Matricula** | `secretaria`, `sistema` | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | `Enrollment.state == SUSPENDED`; exige justificativa; politicas externas permitem reativacao | `ENROLLMENT_REACTIVATE` |
| **Cancelar Matricula** | `secretaria`, `suporte_adm`, `sistema` | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | Apenas em janelas permitidas; exige justificativa | `ENROLLMENT_CANCEL` |
| **Cadastrar Estudante** | `secretaria`, `direcao_estrategica` | Estudantes do proprio tenant | `target.institution_id == actor.institution_id` | Unicidade conforme politica de cadastro | `STUDENT_CREATE` |
| **Cadastrar Professor** | `secretaria`, `direcao_estrategica` | Professores do proprio tenant | `target.institution_id == actor.institution_id` | Unicidade conforme politica institucional | `TEACHER_CREATE` |
| **Cadastrar Responsavel e Vincular ao Estudante** | `secretaria`, `direcao_estrategica` | Responsaveis e vinculos com estudantes do proprio tenant | `target.institution_id == actor.institution_id` | Estudante existe; relacao permitida pela politica institucional | `GUARDIAN_CREATE` |
| **Criar Ano Letivo e Periodos** | `direcao_estrategica`, `secretaria` | Estrutura academica do proprio tenant | `target.institution_id == actor.institution_id` | `secretaria` apenas com permissao ampliada; sem conflito estrutural; politica de calendario valida | `SCHOOL_YEAR_CREATE` |
| **Criar Turma** | `secretaria`, `direcao_estrategica` | Turmas do proprio tenant | `target.institution_id == actor.institution_id` | Ano e periodo existem; chave de negocio unica no escopo | `CLASS_GROUP_CREATE` |
| **Associar Professor a Disciplina e Turma** | `secretaria`, `coordenacao`, `direcao_estrategica` | Atribuicoes docentes do proprio tenant | `target.institution_id == actor.institution_id` | Professor, disciplina e turma existem; vinculo permitido pela politica institucional | `TEACHER_ASSIGN` |
| **Registrar Aula** | `professor`, `coordenacao` | Aulas das proprias atribuicoes ou fluxo de correcao autorizado | `target.course_id == actor.membership.course_id` | Aula dentro da janela permitida; `coordenacao` apenas em fluxo de correcao ou retificacao autorizado | `LESSON_RECORD` |
| **Lancar Frequencia** | `professor`, `coordenacao` | Frequencias das proprias atribuicoes ou fluxo de retificacao autorizado | `target.course_id == actor.membership.course_id` | Aula existe; janela aberta ou permissao de retificacao; estudantes pertencem a turma ou aula | `ATTENDANCE_RECORD` |
| **Lancar Avaliacao e Notas** | `professor`, `coordenacao` | Avaliacoes e notas das proprias atribuicoes | `target.course_id == actor.membership.course_id` | Regime avaliativo vigente permite; janela aberta ou permissao de retificacao | `GRADE_RECORD` |
| **Fechar Periodo e Calcular Media** | `coordenacao`, `sistema`, `direcao_estrategica` | Periodo do proprio tenant | `target.institution_id == actor.institution_id` | Periodo elegivel; politicas congeladas e resolvidas; dados minimos disponiveis | `PERIOD_CLOSE` |
| **Consultar Boletim do Estudante** | `secretaria`, `coordenacao`, `estudante`, `responsavel`, `sistema` | Boletim do estudante | Recurso pessoal ou `target.institution_id == actor.institution_id` | Politica de visibilidade aplicada; `Membership.state == ACTIVE` quando aplicavel | `GRADEBOOK_STUDENT_READ` |
| **Consultar Painel do Estudante** | `estudante`, `responsavel`, `sistema` | Painel consolidado do estudante | Recurso pessoal ou vinculo valido com o estudante | Metricas oficiais e parciais devem ser distinguidas; filtros validos | `DASHBOARD_STUDENT_READ` |
| **Emitir Boletim Oficial** | `secretaria`, `coordenacao`, `sistema` | Documento oficial do estudante | `target.institution_id == actor.institution_id` | Periodo elegivel ou fechado; dados consolidados disponiveis; emissao auditavel | `REPORT_OFFICIAL_ISSUE` |
| **Emitir Relatorio de Frequencia** | `secretaria`, `coordenacao`, `professor`, `sistema` | Relatorio de frequencia | Professor restrito ao proprio escopo; demais no proprio tenant | Filtros validos; exportacao usa o mesmo criterio da tela | `REPORT_READ` + `REPORT_EXPORT` |
| **Emitir Relatorio de Aulas Registradas** | `coordenacao`, `secretaria`, `professor`, `sistema` | Relatorio de aulas registradas | Professor restrito ao proprio escopo; demais no proprio tenant | Pode incluir pendencias de diario; filtros validos | `REPORT_READ` + `REPORT_EXPORT` |
| **Emitir Relatorio de Desempenho por Disciplina** | `coordenacao`, `secretaria`, `professor`, `sistema` | Relatorio de desempenho por disciplina | Professor restrito ao proprio escopo quando permitido; demais no proprio tenant | Regime avaliativo resolvido para o recorte | `REPORT_READ` + `REPORT_EXPORT` |
| **Validar Doc. Civil** *(futuro)* | `secretaria` | `User.identity` | `target_membership.institution_id == actor.institution_id` | Tarefa de conformidade legal | `USER_IDENTITY_VALIDATE` |
| **Trancar ou Transferir** *(futuro)* | `secretaria` | `Membership` | `target.institution_id == actor.institution_id` | Gestao de ocupacao e fluxo de caixa | `MEMBERSHIP_TRANSFER` |
| **Emitir Certificado** *(futuro)* | `secretaria` | `Membership` | `target.institution_id == actor.institution_id` | Fe publica da secretaria academica | `CERTIFICATE_ISSUE` |
| **Criar Grade Curricular** *(futuro)* | `coordenacao` | `Course`/`Subject` | `target.institution_id == actor.institution_id` | Definicao tecnica de ensino | `CURRICULUM_CREATE` |
| **Aprovar Diario de Classe** *(futuro)* | `coordenacao` | `LessonPlan` | `target.course_id == actor.membership.course_id` | Auditoria da entrega pedagogica | `LESSON_APPROVE` |
| **Auditar Notas** *(futuro)* | `coordenacao` | `Grade` | `target.course_id == actor.membership.course_id` | Garante a integridade pedagogica | `GRADE_AUDIT` |
| **Trocar Papel de Membership** *(futuro)* | `direcao_estrategica`, `administrador_plataforma` | Memberships do proprio tenant ou qualquer `Membership` | `target.institution_id == actor.institution_id` ou sem restricao | Troca auditavel; `role_id` anterior preservado no historico; `course_id` compativel com o novo papel | `MEMBERSHIP_ROLE_CHANGE` |
| **Criar Role** *(futuro)* | `administrador_plataforma` | Catalogo global de papeis | Sem restricao | `code` unico; nivel valido; audit trail obrigatorio | `ROLE_CREATE` |
| **Desativar Role** *(futuro)* | `administrador_plataforma` | Qualquer `Role` | Sem restricao | Papel entra em `INACTIVE`; efeito nao retroativo sobre memberships existentes deve ser auditado | `ROLE_DEACTIVATE` |
| **Reativar Role** *(futuro)* | `administrador_plataforma` | Qualquer `Role` | Sem restricao | `Role.status == INACTIVE`; reativacao auditavel | `ROLE_ACTIVATE` |
| **Configurar Politica Institucional** *(futuro)* | `direcao_estrategica` | Politicas do proprio tenant | `target.institution_id == actor.institution_id` | Alteracoes auditaveis; congelamento por periodo quando aplicavel | `POLICY_CONFIGURE` |

### 4.1. Matriz Espelhada por Ator
A tabela abaixo reproduz a mesma matriz operacional, agora agrupada por ator para consulta direta de responsabilidades e limites de acesso.

#### `administrador_plataforma`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Cadastrar Usuario** | Qualquer `User` | Sem restricao (cross-tenant) | N/A | `USER_CREATE` |
| **Ativar Usuario** | Qualquer `User` | Sem restricao | `User.state == PENDING` | `USER_ACTIVATE` |
| **Desbloquear Usuario** | Qualquer `User` | Sem restricao | `User.state == SUSPENDED`; intervencao de emergencia; audit trail obrigatorio | `USER_UNLOCK` |
| **Suspender Usuario** | Qualquer `User` | Sem restricao | `User.state == ACTIVE`; requer justificativa; audit trail obrigatorio | `USER_SUSPEND` |
| **Encerrar Usuario** | Qualquer `User` | Sem restricao | `User.state in (ACTIVE, SUSPENDED)`; irreversivel; requer justificativa | `USER_CLOSE` |
| **Vincular Usuario a Instituicao** | Qualquer vinculo | Sem restricao | `User.state == ACTIVE` | `MEMBERSHIP_CREATE` |
| **Ativar Membership** | Qualquer `Membership` | Sem restricao | `Membership.state == SUSPENDED` | `MEMBERSHIP_ACTIVATE` |
| **Encerrar Membership** | Qualquer `Membership` | Sem restricao | `Membership.state in (ACTIVE, SUSPENDED)`; irreversivel; requer justificativa | `MEMBERSHIP_CLOSE` |
| **Cadastrar Instituicao** *(organizacional)* | Nova `Institution` | Sem restricao (cross-tenant) | Cria o tenant; dados minimos obrigatorios | `INSTITUTION_CREATE` |
| **Cadastrar Rede, Instituicao e Unidade** | Estrutura organizacional global | Sem restricao (cross-tenant) | Duplicidade organizacional resolvida; politica de cadastro organizacional aplicada | `NETWORK_STRUCTURE_CREATE` |
| **Trocar Papel de Membership** *(futuro)* | Memberships do proprio tenant ou qualquer `Membership` | `target.institution_id == actor.institution_id` ou sem restricao | Troca auditavel; `role_id` anterior preservado no historico; `course_id` compativel com o novo papel | `MEMBERSHIP_ROLE_CHANGE` |
| **Criar Role** *(futuro)* | Catalogo global de papeis | Sem restricao | `code` unico; nivel valido; audit trail obrigatorio | `ROLE_CREATE` |
| **Desativar Role** *(futuro)* | Qualquer `Role` | Sem restricao | Papel entra em `INACTIVE`; efeito nao retroativo sobre memberships existentes deve ser auditado | `ROLE_DEACTIVATE` |
| **Reativar Role** *(futuro)* | Qualquer `Role` | Sem restricao | `Role.status == INACTIVE`; reativacao auditavel | `ROLE_ACTIVATE` |

#### `direcao_estrategica`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Cadastrar Usuario** | Equipe da instituicao | `target_membership.institution_id == actor.institution_id` | Fluxo composto de onboarding institucional | `USER_CREATE` + `MEMBERSHIP_CREATE` |
| **Ativar Usuario** | Usuarios do proprio tenant | `target_membership.institution_id == actor.institution_id` | `User.state == PENDING` | `USER_ACTIVATE` |
| **Desbloquear Usuario** | Usuarios do proprio tenant | `target_membership.institution_id == actor.institution_id` | `User.state == SUSPENDED` | `USER_UNLOCK` |
| **Vincular Usuario a Instituicao** | Vinculos do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == ACTIVE` | `MEMBERSHIP_CREATE` |
| **Ativar Membership** | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == SUSPENDED` | `MEMBERSHIP_ACTIVATE` |
| **Suspender Membership** | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == ACTIVE`; requer justificativa | `MEMBERSHIP_SUSPEND` |
| **Encerrar Membership** | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state in (ACTIVE, SUSPENDED)`; irreversivel; requer justificativa | `MEMBERSHIP_CLOSE` |
| **Configurar Instituicao** *(organizacional)* | Propria `Institution` | `target.institution_id == actor.institution_id` | Perfil, endereco, contato, logo | `INSTITUTION_CONFIGURE` |
| **Cadastrar Estudante** | Estudantes do proprio tenant | `target.institution_id == actor.institution_id` | Unicidade conforme politica de cadastro | `STUDENT_CREATE` |
| **Cadastrar Professor** | Professores do proprio tenant | `target.institution_id == actor.institution_id` | Unicidade conforme politica institucional | `TEACHER_CREATE` |
| **Cadastrar Responsavel e Vincular ao Estudante** | Responsaveis e vinculos com estudantes do proprio tenant | `target.institution_id == actor.institution_id` | Estudante existe; relacao permitida pela politica institucional | `GUARDIAN_CREATE` |
| **Criar Ano Letivo e Periodos** | Estrutura academica do proprio tenant | `target.institution_id == actor.institution_id` | `secretaria` apenas com permissao ampliada; sem conflito estrutural; politica de calendario valida | `SCHOOL_YEAR_CREATE` |
| **Criar Turma** | Turmas do proprio tenant | `target.institution_id == actor.institution_id` | Ano e periodo existem; chave de negocio unica no escopo | `CLASS_GROUP_CREATE` |
| **Associar Professor a Disciplina e Turma** | Atribuicoes docentes do proprio tenant | `target.institution_id == actor.institution_id` | Professor, disciplina e turma existem; vinculo permitido pela politica institucional | `TEACHER_ASSIGN` |
| **Fechar Periodo e Calcular Media** | Periodo do proprio tenant | `target.institution_id == actor.institution_id` | Periodo elegivel; politicas congeladas e resolvidas; dados minimos disponiveis | `PERIOD_CLOSE` |
| **Trocar Papel de Membership** *(futuro)* | Memberships do proprio tenant ou qualquer `Membership` | `target.institution_id == actor.institution_id` ou sem restricao | Troca auditavel; `role_id` anterior preservado no historico; `course_id` compativel com o novo papel | `MEMBERSHIP_ROLE_CHANGE` |
| **Configurar Politica Institucional** *(futuro)* | Politicas do proprio tenant | `target.institution_id == actor.institution_id` | Alteracoes auditaveis; congelamento por periodo quando aplicavel | `POLICY_CONFIGURE` |

#### `gestao_financeira`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Ativar Membership** | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == SUSPENDED`; reativacao apos confirmacao de pagamento | `MEMBERSHIP_ACTIVATE` |
| **Suspender Membership** | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == ACTIVE`; inadimplencia; requer justificativa | `MEMBERSHIP_SUSPEND` |

#### `secretaria`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Cadastrar Usuario** | Alunos e responsaveis | `target_membership.institution_id == actor.institution_id` | `target.role` deve ter nivel inferior ao da secretaria; `User` e `Membership` devem nascer na mesma transacao | `USER_CREATE` + `MEMBERSHIP_CREATE` |
| **Configurar Instituicao** *(organizacional)* | Propria `Institution` | `target.institution_id == actor.institution_id` | Delegado pela `direcao_estrategica` | `INSTITUTION_CONFIGURE` |
| **Criar Matricula** | Alunos do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == ACTIVE`, `Membership.state == ACTIVE` | `ENROLLMENT_CREATE` |
| **Consultar Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | N/A | `ENROLLMENT_READ` |
| **Listar Historico de Matricula** | Historico append-only da matricula | `target.institution_id == actor.institution_id` | Acesso a trilha de auditoria permitido | `ENROLLMENT_HISTORY_READ` |
| **Suspender Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | `Enrollment.state == ACTIVE`; exige justificativa; politicas externas permitem suspensao | `ENROLLMENT_SUSPEND` |
| **Reativar Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | `Enrollment.state == SUSPENDED`; exige justificativa; politicas externas permitem reativacao | `ENROLLMENT_REACTIVATE` |
| **Cancelar Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | Apenas em janelas permitidas; exige justificativa | `ENROLLMENT_CANCEL` |
| **Cadastrar Estudante** | Estudantes do proprio tenant | `target.institution_id == actor.institution_id` | Unicidade conforme politica de cadastro | `STUDENT_CREATE` |
| **Cadastrar Professor** | Professores do proprio tenant | `target.institution_id == actor.institution_id` | Unicidade conforme politica institucional | `TEACHER_CREATE` |
| **Cadastrar Responsavel e Vincular ao Estudante** | Responsaveis e vinculos com estudantes do proprio tenant | `target.institution_id == actor.institution_id` | Estudante existe; relacao permitida pela politica institucional | `GUARDIAN_CREATE` |
| **Criar Ano Letivo e Periodos** | Estrutura academica do proprio tenant | `target.institution_id == actor.institution_id` | `secretaria` apenas com permissao ampliada; sem conflito estrutural; politica de calendario valida | `SCHOOL_YEAR_CREATE` |
| **Criar Turma** | Turmas do proprio tenant | `target.institution_id == actor.institution_id` | Ano e periodo existem; chave de negocio unica no escopo | `CLASS_GROUP_CREATE` |
| **Associar Professor a Disciplina e Turma** | Atribuicoes docentes do proprio tenant | `target.institution_id == actor.institution_id` | Professor, disciplina e turma existem; vinculo permitido pela politica institucional | `TEACHER_ASSIGN` |
| **Consultar Boletim do Estudante** | Boletim do estudante | Recurso pessoal ou `target.institution_id == actor.institution_id` | Politica de visibilidade aplicada; `Membership.state == ACTIVE` quando aplicavel | `GRADEBOOK_STUDENT_READ` |
| **Emitir Boletim Oficial** | Documento oficial do estudante | `target.institution_id == actor.institution_id` | Periodo elegivel ou fechado; dados consolidados disponiveis; emissao auditavel | `REPORT_OFFICIAL_ISSUE` |
| **Emitir Relatorio de Frequencia** | Relatorio de frequencia | Professor restrito ao proprio escopo; demais no proprio tenant | Filtros validos; exportacao usa o mesmo criterio da tela | `REPORT_READ` + `REPORT_EXPORT` |
| **Emitir Relatorio de Aulas Registradas** | Relatorio de aulas registradas | Professor restrito ao proprio escopo; demais no proprio tenant | Pode incluir pendencias de diario; filtros validos | `REPORT_READ` + `REPORT_EXPORT` |
| **Emitir Relatorio de Desempenho por Disciplina** | Relatorio de desempenho por disciplina | Professor restrito ao proprio escopo quando permitido; demais no proprio tenant | Regime avaliativo resolvido para o recorte | `REPORT_READ` + `REPORT_EXPORT` |
| **Validar Doc. Civil** *(futuro)* | `User.identity` | `target_membership.institution_id == actor.institution_id` | Tarefa de conformidade legal | `USER_IDENTITY_VALIDATE` |
| **Trancar ou Transferir** *(futuro)* | `Membership` | `target.institution_id == actor.institution_id` | Gestao de ocupacao e fluxo de caixa | `MEMBERSHIP_TRANSFER` |
| **Emitir Certificado** *(futuro)* | `Membership` | `target.institution_id == actor.institution_id` | Fe publica da secretaria academica | `CERTIFICATE_ISSUE` |

#### `coordenacao`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Consultar Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | N/A | `ENROLLMENT_READ` |
| **Listar Historico de Matricula** | Historico append-only da matricula | `target.institution_id == actor.institution_id` | Acesso a trilha de auditoria permitido | `ENROLLMENT_HISTORY_READ` |
| **Associar Professor a Disciplina e Turma** | Atribuicoes docentes do proprio tenant | `target.institution_id == actor.institution_id` | Professor, disciplina e turma existem; vinculo permitido pela politica institucional | `TEACHER_ASSIGN` |
| **Registrar Aula** | Aulas das proprias atribuicoes ou fluxo de correcao autorizado | `target.course_id == actor.membership.course_id` | Aula dentro da janela permitida; `coordenacao` apenas em fluxo de correcao ou retificacao autorizado | `LESSON_RECORD` |
| **Lancar Frequencia** | Frequencias das proprias atribuicoes ou fluxo de retificacao autorizado | `target.course_id == actor.membership.course_id` | Aula existe; janela aberta ou permissao de retificacao; estudantes pertencem a turma ou aula | `ATTENDANCE_RECORD` |
| **Lancar Avaliacao e Notas** | Avaliacoes e notas das proprias atribuicoes | `target.course_id == actor.membership.course_id` | Regime avaliativo vigente permite; janela aberta ou permissao de retificacao | `GRADE_RECORD` |
| **Fechar Periodo e Calcular Media** | Periodo do proprio tenant | `target.institution_id == actor.institution_id` | Periodo elegivel; politicas congeladas e resolvidas; dados minimos disponiveis | `PERIOD_CLOSE` |
| **Consultar Boletim do Estudante** | Boletim do estudante | Recurso pessoal ou `target.institution_id == actor.institution_id` | Politica de visibilidade aplicada; `Membership.state == ACTIVE` quando aplicavel | `GRADEBOOK_STUDENT_READ` |
| **Emitir Boletim Oficial** | Documento oficial do estudante | `target.institution_id == actor.institution_id` | Periodo elegivel ou fechado; dados consolidados disponiveis; emissao auditavel | `REPORT_OFFICIAL_ISSUE` |
| **Emitir Relatorio de Frequencia** | Relatorio de frequencia | Professor restrito ao proprio escopo; demais no proprio tenant | Filtros validos; exportacao usa o mesmo criterio da tela | `REPORT_READ` + `REPORT_EXPORT` |
| **Emitir Relatorio de Aulas Registradas** | Relatorio de aulas registradas | Professor restrito ao proprio escopo; demais no proprio tenant | Pode incluir pendencias de diario; filtros validos | `REPORT_READ` + `REPORT_EXPORT` |
| **Emitir Relatorio de Desempenho por Disciplina** | Relatorio de desempenho por disciplina | Professor restrito ao proprio escopo quando permitido; demais no proprio tenant | Regime avaliativo resolvido para o recorte | `REPORT_READ` + `REPORT_EXPORT` |
| **Criar Grade Curricular** *(futuro)* | `Course`/`Subject` | `target.institution_id == actor.institution_id` | Definicao tecnica de ensino | `CURRICULUM_CREATE` |
| **Aprovar Diario de Classe** *(futuro)* | `LessonPlan` | `target.course_id == actor.membership.course_id` | Auditoria da entrega pedagogica | `LESSON_APPROVE` |
| **Auditar Notas** *(futuro)* | `Grade` | `target.course_id == actor.membership.course_id` | Garante a integridade pedagogica | `GRADE_AUDIT` |

#### `suporte_adm`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Desbloquear Usuario** | Usuarios do proprio tenant | `target_membership.institution_id == actor.institution_id` | `User.state == SUSPENDED`; requer autorizacao explicita | `USER_UNLOCK` |
| **Configurar Instituicao** *(organizacional)* | Propria `Institution` | `target.institution_id == actor.institution_id` | Delegado pela `direcao_estrategica` | `INSTITUTION_CONFIGURE` |
| **Consultar Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | N/A | `ENROLLMENT_READ` |
| **Listar Historico de Matricula** | Historico append-only da matricula | `target.institution_id == actor.institution_id` | Acesso a trilha de auditoria permitido | `ENROLLMENT_HISTORY_READ` |
| **Cancelar Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | Apenas em janelas permitidas; exige justificativa | `ENROLLMENT_CANCEL` |

#### `professor`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Registrar Aula** | Aulas das proprias atribuicoes ou fluxo de correcao autorizado | `target.course_id == actor.membership.course_id` | Aula dentro da janela permitida; `coordenacao` apenas em fluxo de correcao ou retificacao autorizado | `LESSON_RECORD` |
| **Lancar Frequencia** | Frequencias das proprias atribuicoes ou fluxo de retificacao autorizado | `target.course_id == actor.membership.course_id` | Aula existe; janela aberta ou permissao de retificacao; estudantes pertencem a turma ou aula | `ATTENDANCE_RECORD` |
| **Lancar Avaliacao e Notas** | Avaliacoes e notas das proprias atribuicoes | `target.course_id == actor.membership.course_id` | Regime avaliativo vigente permite; janela aberta ou permissao de retificacao | `GRADE_RECORD` |
| **Emitir Relatorio de Frequencia** | Relatorio de frequencia | Professor restrito ao proprio escopo; demais no proprio tenant | Filtros validos; exportacao usa o mesmo criterio da tela | `REPORT_READ` + `REPORT_EXPORT` |
| **Emitir Relatorio de Aulas Registradas** | Relatorio de aulas registradas | Professor restrito ao proprio escopo; demais no proprio tenant | Pode incluir pendencias de diario; filtros validos | `REPORT_READ` + `REPORT_EXPORT` |
| **Emitir Relatorio de Desempenho por Disciplina** | Relatorio de desempenho por disciplina | Professor restrito ao proprio escopo quando permitido; demais no proprio tenant | Regime avaliativo resolvido para o recorte | `REPORT_READ` + `REPORT_EXPORT` |

#### `estudante`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Consultar Boletim do Estudante** | Boletim do estudante | Recurso pessoal ou `target.institution_id == actor.institution_id` | Politica de visibilidade aplicada; `Membership.state == ACTIVE` quando aplicavel | `GRADEBOOK_STUDENT_READ` |
| **Consultar Painel do Estudante** | Painel consolidado do estudante | Recurso pessoal ou vinculo valido com o estudante | Metricas oficiais e parciais devem ser distinguidas; filtros validos | `DASHBOARD_STUDENT_READ` |

#### `responsavel`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Consultar Boletim do Estudante** | Boletim do estudante | Recurso pessoal ou `target.institution_id == actor.institution_id` | Politica de visibilidade aplicada; `Membership.state == ACTIVE` quando aplicavel | `GRADEBOOK_STUDENT_READ` |
| **Consultar Painel do Estudante** | Painel consolidado do estudante | Recurso pessoal ou vinculo valido com o estudante | Metricas oficiais e parciais devem ser distinguidas; filtros validos | `DASHBOARD_STUDENT_READ` |

#### `sistema`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Cadastrar Usuario** | Alunos | Baseado no contrato do gateway de pagamento | Fluxo tecnico auditavel | `USER_CREATE` + `MEMBERSHIP_CREATE` |
| **Criar Matricula** | Alunos do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == ACTIVE`, `Membership.state == ACTIVE` | `ENROLLMENT_CREATE` |
| **Consultar Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | N/A | `ENROLLMENT_READ` |
| **Listar Historico de Matricula** | Historico append-only da matricula | `target.institution_id == actor.institution_id` | Acesso a trilha de auditoria permitido | `ENROLLMENT_HISTORY_READ` |
| **Suspender Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | `Enrollment.state == ACTIVE`; exige justificativa; politicas externas permitem suspensao | `ENROLLMENT_SUSPEND` |
| **Reativar Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | `Enrollment.state == SUSPENDED`; exige justificativa; politicas externas permitem reativacao | `ENROLLMENT_REACTIVATE` |
| **Cancelar Matricula** | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | Apenas em janelas permitidas; exige justificativa | `ENROLLMENT_CANCEL` |
| **Fechar Periodo e Calcular Media** | Periodo do proprio tenant | `target.institution_id == actor.institution_id` | Periodo elegivel; politicas congeladas e resolvidas; dados minimos disponiveis | `PERIOD_CLOSE` |
| **Consultar Boletim do Estudante** | Boletim do estudante | Recurso pessoal ou `target.institution_id == actor.institution_id` | Politica de visibilidade aplicada; `Membership.state == ACTIVE` quando aplicavel | `GRADEBOOK_STUDENT_READ` |
| **Consultar Painel do Estudante** | Painel consolidado do estudante | Recurso pessoal ou vinculo valido com o estudante | Metricas oficiais e parciais devem ser distinguidas; filtros validos | `DASHBOARD_STUDENT_READ` |
| **Emitir Boletim Oficial** | Documento oficial do estudante | `target.institution_id == actor.institution_id` | Periodo elegivel ou fechado; dados consolidados disponiveis; emissao auditavel | `REPORT_OFFICIAL_ISSUE` |
| **Emitir Relatorio de Frequencia** | Relatorio de frequencia | Professor restrito ao proprio escopo; demais no proprio tenant | Filtros validos; exportacao usa o mesmo criterio da tela | `REPORT_READ` + `REPORT_EXPORT` |
| **Emitir Relatorio de Aulas Registradas** | Relatorio de aulas registradas | Professor restrito ao proprio escopo; demais no proprio tenant | Pode incluir pendencias de diario; filtros validos | `REPORT_READ` + `REPORT_EXPORT` |
| **Emitir Relatorio de Desempenho por Disciplina** | Relatorio de desempenho por disciplina | Professor restrito ao proprio escopo quando permitido; demais no proprio tenant | Regime avaliativo resolvido para o recorte | `REPORT_READ` + `REPORT_EXPORT` |

#### `integracao_autorizada`
| Caso de Uso | Alvo | Validacao de Escopo | Condicao Adicional | Capability requerida |
| :--- | :--- | :--- | :--- | :--- |
| **Criar Matricula** | Alunos do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == ACTIVE`, `Membership.state == ACTIVE` | `ENROLLMENT_CREATE` |

---

## 5. Diretrizes de Design e Seguranca

### 5.1. Pipeline de Validacao em Linha (Early Return)
Toda requisicao que adentra o barramento da aplicacao deve passar obrigatoriamente pela seguinte esteira sequencial de avaliacao de curto-circuito:

```text
[Requisicao Entrada]
         |
         v
 1. Autenticacao Global ---> Se User.state != ACTIVE ---> Retorna 423 Locked
         |
         v
 2. Isolamento de Tenant --> Se Tenant_ID incompativel --> Retorna 403 Forbidden
         |
         v
 3. Escopo Funcional -----> Se principal nao possui Capability --> Retorna 403 Forbidden
         |
         v
 4. Predicado de Atributo -> Se course_id divergente -------> Retorna 403 Forbidden
         |
         v
[Executa Caso de Uso]
```

**Implementacao Django/Python - Evitando Queries Redundantes:**
As verificacoes dos passos 1 e 2 (`User.state` e `Membership.state`) devem ocorrer uma unica vez no **middleware de autenticacao/captura de tenant**, populando `request.user` e `request.membership` antes de qualquer use case ser executado. A camada de Application recebe esses objetos ja validados e foca no **Predicado de Atribuicao** (passo 4) e nos escopos granulares do caso de uso via `role.has_capability(Capability.X)` para atores humanos ou conjunto tecnico equivalente para service accounts. Isso elimina queries redundantes ao banco a cada verificacao de acesso.

### 5.2. Identidade de Servico (Service Accounts)
* Devem possuir identificadores unicos e nao compartilhados.
* Toda chamada efetuada pelo ator `sistema` deve usar tokens assinados internamente de escopo restrito.
* O payload do comando deve conter metadados identificando a origem do disparo (`job_name`, `execution_id`, `timestamp`).
* Service accounts nao instanciam `Role` via aggregate institucional; elas recebem um conjunto tecnico explicito de `Capabilities` por contrato.
* **Audit Trail:** Toda acao disparada pelo ator `sistema` deve registrar o ID da rotina e o timestamp original.
* E expressamente proibido que rotinas automaticas contornem as invariantes de validacao de estado do Dominio.
* Proibido o uso de credenciais de servico para acesso via interface de usuario (UI).

### 5.3. Codigos de Erro Padronizados
A camada de Application nao deve expor mensagens nativas do banco ou do framework. Os erros de autorizacao devem seguir estritamente o catalogo estruturado:

* `AUTHZ_IDENTITY_LOCKED`: Login ou identidade global suspensa ou inativa.
* `AUTHZ_TENANT_BREACH`: Tentativa ilegal de travessia de fronteira entre instituicoes (cross-tenant injection).
* `AUTHZ_MISSING_CAPABILITY`: O principal autenticado nao possui a `Capability` necessaria para a operacao.
* `AUTHZ_ATTRIBUTE_MISMATCH`: O usuario tem o papel correto, mas nao possui atribuicao para o objeto especifico (ex: professor tentando lancar nota em turma onde nao tem vinculo).
* `AUTHZ_TEMPORAL_CONSTRAINT`: Operacao bloqueada por regras cronologicas (janela letiva fechada, periodo encerrado).

---

## 6. Estrategia de Testes Automatizados

A robustez desta politica deve ser garantida por uma suite de testes de integracao:

* **Caminho Feliz:** Ator com papel e escopo corretos executa a acao com sucesso.
* **Falha de Papel:** Usuario autenticado, mas com papel insuficiente (ex: estudante tentando cancelar matricula).
* **Falha de Fronteira (Multi-tenancy):** Secretaria da Instituicao A tentando listar alunos da Instituicao B.
* **Falha de Estado:** Usuario com papel correto, mas em estado `SUSPENDED`, deve ter acesso negado.
* **Falha de Atribuicao:** Professor tentando lancar nota em curso onde nao possui vinculo.

---

## 7. Encerramento, LGPD e Preservacao de Historico

O caso de uso **Encerrar** (`User` ou `Membership`) e mapeado como **Soft Delete / Anonimizacao**, nunca como exclusao fisica de registros.

### Encerrar Membership
- `Membership.state` transiciona para `INACTIVE` (estado terminal).
- O historico de matriculas, notas e frequencias vinculadas ao `Membership` e preservado integralmente - obrigacao legal de guarda de registros academicos.
- Nenhum dado e deletado fisicamente.

### Encerrar User
- `User.state` transiciona para `INACTIVE` (estado terminal).
- Dados de identificacao pessoal (nome, email, CPF) podem ser anonimizados sob demanda explicita do titular (direito ao esquecimento - LGPD Art. 18).
- O historico academico e financeiro associado e preservado em forma anonimizada para cumprir obrigacoes legais de guarda.
- A anonimizacao e um processo separado, acionado pela `direcao_estrategica` ou `administrador_plataforma`, e nao ocorre automaticamente com o encerramento.

---

## 8. Evolucao e Auditoria
* **Logs:** Toda negacao de acesso (403) deve ser logada com o contexto completo (`User ID`, `Role ID`, `Resource ID`, `Scope Requested`).
* **Revisao:** Esta matriz e o ADR 034 devem ser revisados semestralmente ou a cada novo modulo critico adicionado ao sistema.
