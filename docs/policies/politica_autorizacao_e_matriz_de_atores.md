# 🏛️ Política de Autorização e Governança de Acesso

## 1. Objetivo
Estabelecer as diretrizes de controle de acesso para a plataforma, garantindo o **Princípio do Menor Privilégio**. Esta política define a **relação tridimensional** entre **Atores** (`Roles`), **Casos de Uso** (`Capabilities`) e os limites de seus **Escopos** (`Tenants`/`Courses`), servindo como **especificação executável** para engenharia e testes. O sistema adota um modelo híbrido de autorização baseado em papéis (**RBAC**) com validação de escopos e atributos (**ABAC**).

---

## 2. Taxonomia de Atores

### Nivel 0: Plataforma (Cross-Tenant)
* **`administrador_plataforma`** — Superusuário do SaaS. Não possui `Membership`. Identificado pelo sinalizador `is_superuser` no mecanismo de autenticação. Escopo global, irrestrito entre tenants. Responsável pela saúde do software, criação de instituições e gestão de recursos globais.

### Nivel 1: Estratégico Institucional
* **`direcao_estrategica`** — `Membership` com `course_id = null`. Autoridade de governança institucional: configuração do tenant, concessão e revogação de papéis, gestão de identidade e vínculos. Inclui: Diretor Geral e cargos equivalentes.
* **`gestao_financeira`** — `Membership` com `course_id = null`. Autoridade sobre saúde financeira da instituição. Único papel que pode suspender `Membership` por inadimplência e reativá-lo após confirmação de pagamento. Inclui: Controller Financeiro e cargos equivalentes. *(escopo financeiro completo previsto para Fase 2)*

### Nivel 2: Operacional Interno
* **`secretaria`** — Guardiã do vínculo legal e contratual (`Enrollment`/`Membership`). Atua no ciclo de vida de entrada e saída do usuário no ecossistema (matrículas, transferências, emissão de documentos oficiais). Escopo institucional ou por curso.
* **`coordenacao`** — Guardiã da qualidade de ensino e conformidade curricular. Foco no Conteúdo (`Course`/`Subject`) e no Desempenho (`Grades`/`Calendar`). Responsável pelo fechamento de períodos, aprovação de diários e alocação docente. Escopo institucional ou por curso.
* **`suporte_adm`** — Operador administrativo com escopos restritos e permissões pontuais delegadas pela `direcao_estrategica`.

### Nivel 3: Execução Curricular
* **`professor`** — Escopo sempre restrito ao `course_id` das próprias atribuições ativas de componentes curriculares.

### Nivel 4: Utilizador Final
* **`estudante`** — Acesso estritamente pessoal (self-service) aos próprios registros acadêmicos e financeiros.
* **`responsavel`** — Acesso limitado aos dados dos estudantes vinculados via `guardian_id`.

### Autômatos e Serviços
* **`sistema`** — Jobs agendados e rotinas de consolidação de dados. Deve registrar ID da rotina e timestamp em toda ação.
* **`integracao_autorizada`** — APIs de terceiros e sistemas parceiros com credenciais dedicadas.

---

## 3. Modelo de Dados de Autorização (ERD Conceitual)

### Relacionamentos principais

```
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
                                      | (mapa estático no Domínio — não persistido em banco)
                                      |
                            +---------+---------+
                            |    Capability     |
                            | (StrEnum no       |
                            |   Domínio)        |
                            +-------------------+
```

- Um `User` pode ter múltiplos `Membership` (um por instituição/curso)
- Uma `Institution` pode ter múltiplos `Membership` (um por usuário/curso)
- Um `Role` define o conjunto de `Capabilities` que o `Membership` herda
- `Capabilities` são um mapa estático no domínio (`frozenset[Capability]` computado a partir de `Role.code`) — não são armazenadas em banco de dados
- O `Membership` referencia `Role` pelo `role_id` — não carrega escopos diretamente

### Edge Cases documentados

**Administrador da Plataforma**
Não possui `Membership`. Identificado pelo sinalizador `is_superuser` no mecanismo de autenticação (Django auth). A camada de autorização verifica esse sinalizador antes de exigir `Membership`, concedendo acesso global irrestrito.

**Aluno Menor de Idade**
O campo `guardian_id` pertence ao aggregate `User` (identidade), não ao `Membership` (vínculo). O responsável legal é o mesmo independente da escola em que o aluno estiver matriculado.

**Troca de Escola**
Quando um aluno muda de instituição, o `Membership` anterior transiciona para `INACTIVE` e um novo `Membership` é criado na nova instituição. O histórico do vínculo anterior é preservado nativamente. Nenhum dado é apagado.

**Suspensão por Inadimplência (`gestao_financeira`)**
A `gestao_financeira` suspende o `Membership.state` (vínculo institucional), nunca o `User.state` (identidade global). Se o mesmo aluno estiver matriculado na Escola A e na Escola B, a inadimplência na Escola A suspende apenas o `Membership` da Escola A — o acesso à Escola B permanece intacto. O `User` continua `ACTIVE`. Isso garante que a identidade global não seja penalizada por conflitos financeiros de um tenant específico.

---

## 4. Matriz de Autorização Operacional
A autorização é validada na camada de **Application**, antes da execução de qualquer lógica de domínio.

| Caso de Uso | Ator | Alvo | Validacao de Escopo | Condicao Adicional |
| :--- | :--- | :--- | :--- | :--- |
| **Cadastrar Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao (cross-tenant) | N/A |
| **Cadastrar Usuario** | `direcao_estrategica` | Equipe da instituicao | `target.institution_id == actor.institution_id` | N/A |
| **Cadastrar Usuario** | `secretaria` | Alunos e responsaveis | `target.role` deve ter nível inferior ao da secretaria | User e Membership institucional devem ser criados na mesma transação para evitar User órfão no sistema |
| **Cadastrar Usuario** | `sistema` | Alunos | Baseado no contrato do gateway de pagamento | N/A |
| **Ativar Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao | `User.state == PENDING` |
| **Ativar Usuario** | `direcao_estrategica` | Usuarios do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == PENDING` |
| **Desbloquear Usuario** | `direcao_estrategica` | Usuarios do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == SUSPENDED` |
| **Desbloquear Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao | `User.state == SUSPENDED`; intervencao de emergencia; audit trail obrigatorio |
| **Desbloquear Usuario** | `suporte_adm` | Usuarios do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == SUSPENDED`; requer autorizacao explicita |
| **Vincular Usuario a Instituicao** | `administrador_plataforma` | Qualquer vinculo | Sem restricao | `User.state == ACTIVE` |
| **Vincular Usuario a Instituicao** | `direcao_estrategica` | Vinculos do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == ACTIVE` |
| **Ativar Membership** | `administrador_plataforma` | Qualquer `Membership` | Sem restricao | `Membership.state == SUSPENDED` |
| **Ativar Membership** | `direcao_estrategica` | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == SUSPENDED` |
| **Ativar Membership** | `gestao_financeira` | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == SUSPENDED`; reativacao apos confirmacao de pagamento |
| **Suspender Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao | `User.state == ACTIVE`; requer justificativa; audit trail obrigatorio |
| **Suspender Membership** | `direcao_estrategica` | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == ACTIVE`; requer justificativa |
| **Suspender Membership** | `gestao_financeira` | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state == ACTIVE`; inadimplencia; requer justificativa |
| **Encerrar Membership** | `administrador_plataforma` | Qualquer `Membership` | Sem restricao | `Membership.state in (ACTIVE, SUSPENDED)`; irreversivel; requer justificativa |
| **Encerrar Membership** | `direcao_estrategica` | Memberships do proprio tenant | `target.institution_id == actor.institution_id` | `Membership.state in (ACTIVE, SUSPENDED)`; irreversivel; requer justificativa |
| **Encerrar Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao | `User.state in (ACTIVE, SUSPENDED)`; irreversivel; requer justificativa |
| **Cadastrar Instituicao** *(organizacional)* | `administrador_plataforma` | Nova `Institution` | Sem restricao (cross-tenant) | Cria o tenant; dados minimos obrigatorios |
| **Configurar Instituicao** *(organizacional)* | `direcao_estrategica` | Propria `Institution` | `target.institution_id == actor.institution_id` | Perfil, endereco, contato, logo |
| **Configurar Instituicao** *(organizacional)* | `secretaria`, `suporte_adm` | Propria `Institution` | `target.institution_id == actor.institution_id` | Delegado pela `direcao_estrategica` |
| **Criar Matricula** | `secretaria`, `sistema` | Alunos do proprio tenant | `target.institution_id == actor.institution_id` | `User.state == ACTIVE`, `Membership.state == ACTIVE` |
| **Consultar Matricula** | `secretaria`, `coordenacao`, `suporte_adm`, `sistema` | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | N/A |
| **Suspender/Reativar Matricula** | `secretaria` | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | Exige justificativa |
| **Cancelar Matricula** | `secretaria`, `suporte_adm` | Matriculas do proprio tenant | `target.institution_id == actor.institution_id` | Apenas em janelas permitidas |
| **Concluir Periodo** | `coordenacao`, `sistema` | Periodo do proprio tenant | `target.institution_id == actor.institution_id` | Periodo deve estar ativo |
| **Lancar Notas/Frequencia** | `professor` | Proprias atribuicoes | `target.course_id == actor.membership.course_id` | Dentro da janela letiva |
| **Consultar Boletim** | `estudante`, `responsavel` | Proprio registro | Recurso pessoal | `Membership.state == ACTIVE` |
| **Validar Doc. Civil** *(futuro)* | `secretaria` | `User.identity` | `target.institution_id == actor.institution_id` | Tarefa de conformidade legal |
| **Trancar/Transferir** *(futuro)* | `secretaria` | `Membership` | `target.institution_id == actor.institution_id` | Gestao de ocupacao e fluxo de caixa |
| **Emitir Certificado** *(futuro)* | `secretaria` | `Membership` | `target.institution_id == actor.institution_id` | Fe publica da secretaria academica |
| **Criar Grade Curricular** *(futuro)* | `coordenacao` | `Course`/`Subject` | `target.institution_id == actor.institution_id` | Definicao tecnica de ensino |
| **Aprovar Diario de Classe** *(futuro)* | `coordenacao` | `LessonPlan` | `target.course_id == actor.membership.course_id` | Auditoria da entrega pedagogica |
| **Auditar Notas** *(futuro)* | `coordenacao` | `Grade` | `target.course_id == actor.membership.course_id` | Garante a integridade pedagogica |
| **Alocar Professor** *(futuro)* | `coordenacao` | `Course_Teacher` | `target.institution_id == actor.institution_id` | Decisao de competencia tecnica |

---

## 5. Diretrizes de Design e Segurança

### 5.1. Pipeline de Validação em Linha (Early Return)
Toda requisição que adentra o barramento da aplicação deve passar obrigatoriamente pela seguinte esteira sequencial de avaliação de curto-circuito:

```
[Requisição Entrada]
         │
         ▼
 1. Autenticação Global ───► Se User.state != ACTIVE ───► Retorna 423 Locked
         │
         ▼
 2. Isolamento de Tenant ──► Se Tenant_ID incompatível ─► Retorna 403 Forbidden
         │
         ▼
 3. Escopo Funcional ────► Se Role não possui Capability ─► Retorna 403 Forbidden
         │
         ▼
 4. Predicado de Atributo ─► Se course_id divergente ────► Retorna 403 Forbidden
         │
         ▼
[Executa Caso de Uso]
```

**Implementação Django/Python — Evitando Queries Redundantes:**
As verificações dos passos 1 e 2 (`User.state` e `Membership.state`) devem ocorrer uma única vez no **middleware de autenticação/captura de tenant**, populando `request.user` e `request.membership` antes de qualquer use case ser executado. A camada de Application recebe esses objetos já validados e foca exclusivamente no **Predicado de Atribuição** (passo 4) e nos escopos granulares do caso de uso via `role.has_capability(Capability.X)`. Isso elimina queries redundantes ao banco a cada verificação de acesso.

### 5.2. Identidade de Serviço (Service Accounts)
* Devem possuir identificadores únicos e não compartilhados.
* Toda chamada efetuada pelo ator `sistema` deve usar tokens assinados internamente de escopo restrito.
* O payload do comando deve conter metadados identificando a origem do disparo (`job_name`, `execution_id`, `timestamp`).
* **Audit Trail:** Toda ação disparada pelo ator `sistema` deve registrar o ID da rotina e o timestamp original.
* É expressamente proibido que rotinas automáticas contornem as invariantes de validação de estado do Domínio.
* Proibido o uso de credenciais de serviço para acesso via interface de usuário (UI).

### 5.3. Códigos de Erro Padronizados
A camada de Application não deve expor mensagens nativas do banco ou do framework. Os erros de autorização devem seguir estritamente o catálogo estruturado:

* `AUTHZ_IDENTITY_LOCKED`: Login ou identidade global suspensa ou inativa.
* `AUTHZ_TENANT_BREACH`: Tentativa ilegal de travessia de fronteira entre instituições (cross-tenant injection).
* `AUTHZ_MISSING_CAPABILITY`: O papel do usuário não possui a `Capability` necessária para a operação.
* `AUTHZ_ATTRIBUTE_MISMATCH`: O usuário tem o papel correto, mas não possui atribuição para o objeto específico (ex: professor tentando lançar nota em turma onde não tem vínculo).
* `AUTHZ_TEMPORAL_CONSTRAINT`: Operação bloqueada por regras cronológicas (janela letiva fechada, período encerrado).

---

## 6. Estratégia de Testes Automatizados

A robustez desta política deve ser garantida por uma suíte de testes de integração:

* **Caminho Feliz:** Ator com papel e escopo corretos executa a ação com sucesso.
* **Falha de Papel:** Usuário autenticado, mas com papel insuficiente (ex: Estudante tentando cancelar matrícula).
* **Falha de Fronteira (Multi-tenancy):** Secretaria da Instituição A tentando listar alunos da Instituição B.
* **Falha de Estado:** Usuário com papel correto, mas em estado `SUSPENDED`, deve ter acesso negado.
* **Falha de Atribuição:** Professor tentando lançar nota em curso onde não possui vínculo.

---

## 7. Encerramento, LGPD e Preservação de Histórico

O caso de uso **Encerrar** (User ou Membership) é mapeado como **Soft Delete / Anonimização**, nunca como exclusão física de registros.

### Encerrar Membership
- `Membership.state` transiciona para `INACTIVE` (estado terminal).
- O histórico de matrículas, notas e frequências vinculadas ao `Membership` é preservado integralmente — obrigação legal de guarda de registros acadêmicos.
- Nenhum dado é deletado fisicamente.

### Encerrar User
- `User.state` transiciona para `INACTIVE` (estado terminal).
- Dados de identificação pessoal (nome, email, CPF) podem ser anonimizados sob demanda explícita do titular (direito ao esquecimento — LGPD Art. 18).
- O histórico acadêmico e financeiro associado é preservado em forma anonimizada para cumprir obrigações legais de guarda.
- A anonimização é um processo separado, acionado pela `direcao_estrategica` ou `administrador_plataforma`, e não ocorre automaticamente com o encerramento.

---

## 8. Evolução e Auditoria
* **Logs:** Toda negação de acesso (403) deve ser logada com o contexto completo (User ID, Role ID, Resource ID, Scope Requested).
* **Revisão:** Esta matriz deve ser revisada semestralmente ou a cada novo módulo crítico adicionado ao sistema.
