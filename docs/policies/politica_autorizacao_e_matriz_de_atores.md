Para elevar o seu documento ao nível "ideal" de arquitetura, vamos consolidar a **Matriz de Atores** e a **Política de Autorização** em um único **Documento de Governança de Acesso**.

O objetivo aqui é transformar intenções em **regras de design** que a engenharia possa traduzir em código (filtros, middlewares e testes) sem ambiguidade.

---

# 🏛️ Política de Autorização e Governança de Acesso

## 1. Objetivo
Estabelecer as diretrizes de controle de acesso para o sistema, garantindo o **Princípio do Menor Privilégio**. Esta política define a relação entre **Atores**, **Casos de Uso** e os limites de seus **Escopos**.

---

## 2. Taxonomia de Atores

### Nivel 0: Plataforma (Cross-Tenant)
* **`administrador_plataforma`** — superusuario do SaaS. Nao possui `Membership`. Identificado pelo sinalizador `is_superuser` no mecanismo de autenticacao. Escopo global, irrestrito entre tenants. Responsavel pela saude do software, criacao de instituicoes e gestao de recursos globais.

### Nivel 1: Estrategico Institucional
* **`direcao_estrategica`** (Direcao Estrategica) — Membership com `course_id = null`. Autoridade de governanca institucional: configuracao do tenant, concessao e revogacao de papeis, gestao de identidade e vinculos. Inclui: Diretor Geral e cargos equivalentes.
* **`gestao_financeira`** (Gestao Financeira) — Membership com `course_id = null`. Autoridade sobre saude financeira da instituicao. Unico papel que pode suspender `Membership` por inadimplencia e reativa-lo apos confirmacao de pagamento. Inclui: Controller Financeiro e cargos equivalentes. *(escopo financeiro completo previsto para Fase 2)*

### Nivel 2: Operacional Interno
* **`secretaria`** (Gestao Academico-Administrativa) — guardia do vinculo legal e financeiro. Foco na Pessoa (`User`) e no Contrato (`Membership`/`Enrollment`). Atua na porta de entrada e saida do sistema. Escopo institucional ou por curso.
* **`coordenacao`** (Gestao Pedagogica) — guardia da qualidade de ensino. Foco no Conteudo (`Course`/`Subject`) e no Desempenho (`Grades`/`Calendar`). Atua no meio do processo garantindo as regras de ensino. Escopo institucional ou por curso.
* **`suporte_adm`** — suporte administrativo com escopo restrito.

### Nivel 3: Execucao Curricular
* **`professor`** — escopo sempre restrito ao `course_id` das proprias atribuicoes.

### Nivel 4: Utilizador Final
* **`estudante`** — acesso estritamente pessoal (self-service).
* **`responsavel`** — acesso aos dados dos estudantes vinculados.

### Automatos e Externos
* **`sistema`** — jobs agendados e rotinas de consolidacao. Deve registrar ID da rotina e timestamp em toda acao.
* **`integracao_autorizada`** — APIs de terceiros e sistemas parceiros com credenciais proprias.

---

## 3. Modelo de Dados de Autorizacao (ERD Conceitual)

### Relacionamentos principais

```
User        (1) ----< (N) Membership
Institution (1) ----< (N) Membership
Role        (1) ----< (N) Membership
Role        (1) ----< (N) Permission/Scope
```

- Um `User` pode ter multiplos `Membership` (um por instituicao/curso)
- Uma `Institution` pode ter multiplos `Membership` (um por usuario/curso)
- Um `Role` define a colecao de `Permission/Scope` que o `Membership` herda
- O `Membership` referencia `Role` pelo `role_id` — nao carrega escopos diretamente

### Edge Cases documentados

**Administrador da Plataforma**
Nao possui `Membership`. Identificado pelo sinalizador `is_superuser` no mecanismo de autenticacao (Django auth). A camada de autorizacao verifica esse sinalizador antes de exigir `Membership`, concedendo acesso global irrestrito.

**Aluno Menor de Idade**
O campo `guardian_id` pertence ao aggregate `User` (identidade), nao ao `Membership` (vinculo). O responsavel legal e o mesmo independente da escola em que o aluno estiver matriculado.

**Troca de Escola**
Quando um aluno muda de instituicao, o `Membership` anterior transiciona para `INACTIVE` e um novo `Membership` e criado na nova instituicao. O historico do vinculo anterior e preservado nativamente. Nenhum dado e apagado.

---

## 4. Matriz de Autorização Operacional
A autorização é validada na camada de **Application**, antes da execução de qualquer lógica de domínio.

| Caso de Uso | Ator | Alvo | Validacao de Escopo | Condicao Adicional |
| :--- | :--- | :--- | :--- | :--- |
| **Cadastrar Usuario** | `administrador_plataforma` | Qualquer `User` | Sem restricao (cross-tenant) | N/A |
| **Cadastrar Usuario** | `direcao_estrategica` | Equipe da instituicao | `target.institution_id == actor.institution_id` | N/A |
| **Cadastrar Usuario** | `secretaria` | Alunos e responsaveis | `target.role` deve ser inferior ao nivel da secretaria | N/A |
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

## 4. Regras de Design e Segurança

### 4.1. Validação em Camadas
A autorização deve seguir o fluxo de precedência:
1.  **Estado do Usuário:** Se `User.state != ACTIVE`, todo acesso é negado (403/423).
2.  **Vínculo Institucional:** O ator deve possuir um `Membership` ativo no Tenant alvo.
3.  **Permissão Funcional:** O papel (`Role`) deve conter o escopo necessário para o Caso de Uso.
4.  **Predicado de Atribuição:** Para papéis curriculares, o `course_id` deve coincidir com o recurso acessado.

### 4.2. Identidade de Serviço (Service Accounts)
* Devem possuir identificadores únicos e não compartilhados.
* **Audit Trail:** Toda ação disparada pelo ator `sistema` deve registrar o ID da rotina e o timestamp original.
* Proibido o uso de credenciais de serviço para acesso via interface de usuário (UI).

### 4.3. Códigos de Erro Padronizados
A Application deve retornar erros granulares para facilitar a depuração e o feedback ao usuário:
* `AUTHZ_USER_LOCKED`: Identidade global suspensa.
* `AUTHZ_INSUFFICIENT_PRIVILEGES`: Papel não possui o escopo necessário.
* `AUTHZ_TENANT_MISMATCH`: Tentativa de acesso a dados de outra instituição.
* `AUTHZ_OUTSIDE_WINDOW`: Ação permitida, mas fora do prazo operacional.

---

## 5. Estratégia de Testes Automatizados

A robustez desta política deve ser garantida por uma suíte de testes de integração:

* **✅ Caminho Feliz:** Ator com papel e escopo corretos executa a ação com sucesso.
* **❌ Falha de Papel:** Usuário autenticado, mas com papel insuficiente (ex: Estudante tentando cancelar matrícula).
* **❌ Falha de Fronteira (Multi-tenancy):** Secretaria da Instituição A tentando listar alunos da Instituição B.
* **❌ Falha de Estado:** Usuário com papel correto, mas em estado `SUSPENDED`, deve ter acesso negado.
* **❌ Falha de Atribuição:** Professor tentando lançar nota em curso onde não possui vínculo.

---

## 6. Evolução e Auditoria
* **Logs:** Toda negação de acesso (403) deve ser logada com o contexto completo (User ID, Role ID, Resource ID, Scope Requested).
* **Revisão:** Esta matriz deve ser revisada semestralmente ou a cada novo módulo crítico adicionado ao sistema.

---
