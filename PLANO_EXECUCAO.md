# Plano de Execução — Sistema de Gestão Escolar

## Disponibilidade Semanal

| Dia         | Horário       | Horas |
|-------------|---------------|-------|
| Segunda     | 14:30 – 19:00 | 4.5h  |
| Terça       | 14:30 – 19:00 | 4.5h  |
| Quarta      | 14:30 – 19:00 | 4.5h  |
| Quinta      | 14:30 – 19:00 | 4.5h  |
| Sexta       | 12:00 – 19:00 | 7.0h  |
| Sábado      | 14:00 – 18:00 | 4.0h  |
| **Total**   |               |**29h**|

---

## Estado Atual do Projeto

### Concluído
- Contexto `Enrollment` — domínio, application, infra, testes, CI/CD
- Contexto `User` — domínio completo e testado
- Contexto `User` — application layer completa (port, services, fakes, testes)

### Em andamento
- Contexto `User` — infrastructure (model, mapper, repository, testes de integração)

### Pendente
- `User` infrastructure (model, mapper, repository, testes)
- Contexto `Role` — domínio + testes
- Contexto `Institution + Course` — ADR + domínio + testes
- Contexto `Membership` — domínio + application + infra + testes
- Camada HTTP/API (endpoints básicos)
- Documentação de portfólio (README técnico)

---

## Semana 1 — 29 Abr a 03 Mai

**Meta da semana:** Fechar todos os testes de domínio do `User` e iniciar a Application layer.

---

### Qua 29/04

- [x] Rehydration com ACTIVE sem `activated_at` levanta `DomainError`
- [x] Rehydration com SUSPENDED sem `suspended_at` levanta `DomainError`
- [x] Rehydration com INACTIVE sem `inactivated_at` levanta `DomainError`
- [x] `suspend()` com `justification=""` levanta `JustificationRequiredError`
- [x] `suspend()` com `justification="  "` levanta `JustificationRequiredError`
- [x] `inactivate()` com `justification` vazia levanta `JustificationRequiredError`
- [x] `unlock()` com `justification` vazia levanta `JustificationRequiredError`

---

### Qui 30/04

- [x] `inactivate()` a partir de `PENDING` — happy path
- [x] `inactivate()` a partir de `SUSPENDED` — happy path
- [x] `peek_domain_events()` retorna eventos sem limpar o buffer
- [x] `created_at` naive (sem timezone) é normalizado para UTC na rehydration
- [x] `unlock()` a partir de `PENDING` levanta erro
- [x] `unlock()` a partir de `ACTIVE` levanta erro
- [x] Remover teste duplicado `test_raises_invalid_state_transition` (linha 107)
- [x] Criar com `email=None` funciona (campo opcional)
- [x] Criar adulto sem `guardian_id` funciona (campo opcional para adultos)

---

### Sex 01/05

- [x] Implementar `UserRepository` (port abstrato)
- [x] Implementar `ErrorCodes` (enum de códigos do contexto User)
- [x] Implementar `ApplicationResult` (DTO de retorno dos services)
- [x] Implementar `DomainErrorMapper` (traduz `DomainError` → `ApplicationError`)
- [x] Implementar `PersistenceErrors` (hierarquia de erros de persistência do User)

---

### Sáb 02/05

- [x] Implementar fake `InMemoryUserRepository`
- [x] Implementar `CreateUser` service
- [x] Teste: criação bem-sucedida retorna resultado com sucesso e evento
- [x] Teste: duplicidade levanta erro de duplicação
- [x] Teste: falha técnica de persistência retorna resultado com erro

---

### Dom 03/05

- [x] Implementar `ActivateUser` service
- [x] Testes do `ActivateUser`: sucesso, user não encontrado, transição inválida, falha de persistência
- [x] Implementar `SuspendUser` service
- [x] Testes do `SuspendUser`: sucesso, user não encontrado, transição inválida, falha de persistência
- [x] Commit geral da semana

---

## Semana 2 — 05 Mai a 11 Mai

**Meta da semana:** Concluir Application layer do `User`, iniciar Infrastructure e domínio do `Role`.

---

### Ter 05/05

- [x] Implementar `UnblockUser` service + testes
- [x] Implementar `CloseUser` service + testes
- [x] Application layer do User completa — todos os testes passando

---

### Qua 06/05

- [x] Implementar `UserModel` (Django ORM)
- [x] Implementar `UserTransitionModel` (Django ORM)
- [x] Criar e aplicar migration

---

### Qui 07/05

- [x] Implementar `UserMapper` (domínio ↔ persistence)
- [x] Testar mapper: aggregate → model e model → aggregate

---

### Sex 08/05

- [x] Implementar `DjangoUserRepository.get_by_id()`
- [x] Implementar `DjangoUserRepository.save()`
- [x] Implementar `DjangoUserRepository.create()`

---

### Sáb 09/05

- [x] Teste de integração: criar User no PostgreSQL
- [x] Teste de integração: rehydration via `get_by_id`
- [x] Teste de integração: salvar transição via `save`
- [x] Teste de integração: duplicidade levanta `UserDuplicationError`

---

### Seg 11/05

- [ ] `RoleState` — estados possíveis do Role
- [ ] `Role` aggregate — invariantes e factory method
- [ ] `Role` errors e events
- [ ] Testes de domínio do `Role`
- [ ] Commit geral da semana

---

## Semana 3 — 12 Mai a 18 Mai

**Meta da semana:** Implementar os contextos `Institution` e `Course`.

---

### Ter 12/05

- [ ] ADR para `Institution` — decisões de design documentadas
- [ ] ADR para `Course` — decisões de design documentadas
- [ ] Definir aggregates, value objects e relações

---

### Qua 13/05

- [ ] `Institution` aggregate — invariantes, estados, factory method
- [ ] `Institution` errors e events

---

### Qui 14/05

- [ ] Testes de domínio do `Institution`

---

### Sex 15/05

- [ ] `Course` aggregate — invariantes, factory method
- [ ] `Course` errors e events
- [ ] Testes de domínio do `Course`

---

### Sáb 16/05

- [ ] `InstitutionRepository` + `CourseRepository` (ports)
- [ ] `CreateInstitution` service + fakes + testes básicos
- [ ] `CreateCourse` service + fakes + testes básicos

---

### Seg 18/05

- [ ] `InstitutionModel` + `CourseModel` + migrations
- [ ] Mappers + repositories básicos
- [ ] Commit geral da semana

---

## Semana 4 — 19 Mai a 25 Mai

**Meta da semana:** Implementar o domínio e a application layer do `Membership`.

---

### Ter 19/05

- [ ] `MembershipState` — estados e máquina de transições
- [ ] `MembershipTransition` value object

---

### Qua 20/05

- [ ] `Membership` aggregate — invariantes, factory method
- [ ] `Membership` events e errors

---

### Qui 21/05

- [ ] Testes de domínio do `Membership` (invariants, transitions, events, pull)

---

### Sex 22/05

- [ ] `MembershipRepository` (port)
- [ ] `ErrorCodes` do Membership
- [ ] `DomainErrorMapper` do Membership
- [ ] `PersistenceErrors` do Membership

---

### Sáb 23/05

- [ ] `VincularUsuario` service + fakes + testes
- [ ] `AtivarMembership` service + fakes + testes
- [ ] `SuspenderMembership` service + fakes + testes
- [ ] `EncerrarMembership` service + fakes + testes

---

### Seg 25/05

- [ ] Testes de application do Membership — todos os cenários
- [ ] Commit geral da semana

---

## Semana 5 — 26 Mai a 01 Jun

**Meta da semana:** Fechar `Membership` infrastructure e expor endpoints HTTP básicos.

---

### Ter 26/05

- [ ] `MembershipModel` + migrations
- [ ] `MembershipMapper`

---

### Qua 27/05

- [ ] `DjangoMembershipRepository` — implementação completa
- [ ] Testes de integração do `Membership` (PostgreSQL)

---

### Qui 28/05

- [ ] Endpoint POST `/users/` — criar usuário
- [ ] Endpoint POST `/users/{id}/activate/` — ativar usuário
- [ ] Endpoint POST `/users/{id}/suspend/` — suspender usuário

---

### Sex 29/05

- [ ] Endpoint POST `/enrollments/` — criar matrícula
- [ ] Error handling middleware (traduz `ApplicationError` → resposta HTTP)
- [ ] Testes básicos dos endpoints

---

### Sáb 30/05

- [ ] README técnico: arquitetura, camadas, decisões de design
- [ ] Exemplos de uso (curl ou httpie)
- [ ] Como rodar localmente (setup, migrations, testes)

---

### Seg 01/06

- [ ] Revisão final de código
- [ ] Limpeza: remover arquivos temporários, comentários desnecessários
- [ ] Tag de versão `v1.0-portfolio`
- [ ] Projeto pronto para portfólio

---

## Critério de Portfólio

- [ ] Dois contextos com vertical slice completo (Enrollment + User)
- [ ] Testes unitários de domínio em todos os aggregates
- [ ] Testes de application com fakes (sem banco)
- [ ] Testes de integração com PostgreSQL real
- [ ] Membership operacional (vincula User + Role + Institution)
- [ ] Pelo menos 3 endpoints HTTP documentados e funcionando
- [ ] README explicando arquitetura e decisões de design

---

## Regras de Trabalho

- Commitar ao final de cada sessão ou quando uma entrega do dia estiver completa.
- Se uma tarefa do dia não for concluída, ela passa para o próximo dia antes de iniciar a próxima.
- Marcar os itens concluídos com `[x]` ao longo da sessão.
- Ao retomar após ausência, revisar este plano e atualizar as datas se necessário.
