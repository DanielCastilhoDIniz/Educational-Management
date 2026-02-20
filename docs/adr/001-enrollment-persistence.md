# ADR 001 — Persistência do Aggregate Enrollment (Snapshot + Transition Log)

## Status
Aprovado

## Contexto
Precisamos persistir o aggregate **Enrollment** garantindo integridade de reidratação, auditoria imutável
das mudanças e consistência transacional entre o estado atual e o histórico de transições.

Além disso, o domínio emite eventos internamente durante transições válidas e a publicação externa
deve ocorrer apenas após persistência bem-sucedida, sem acoplar domínio à infraestrutura.

## Decisão
Adotar a estratégia **Snapshot + Log Append-Only**:

- **Enrollment (Snapshot):** armazena o estado atual da matrícula.
- **EnrollmentTransition (Log):** armazena transições como fatos imutáveis (append-only).
- Persistência deve ser **transacional** (1 caso de uso = 1 transação).
- Controle de concorrência por **versionamento otimista** no snapshot.
- Deduplicação de transições por `transition_id` determinístico (ver ADR 002).

## Consequências

### Positivas
- Consultas rápidas por estado atual (snapshot).
- Histórico completo e auditável (log).
- Domínio permanece puro e testável.
- Base segura para publicar eventos após persistência.
- Evolução gradual (possível Outbox/event sourcing parcial sem refatoração total).

### Negativas / Riscos
- Repositório precisa implementar reidratação (snapshot + log).
- Crescimento do log pode exigir otimizações (paginação/estratégias de leitura).
- Exige disciplina: log é append-only e não pode ser “corrigido” por update.

## Regras e Invariantes
- `EnrollmentTransition` é **append-only** (não editar/não deletar).
- `transition_id` é **unique** e determinístico (ADR 002).
- `actor_id` é obrigatório (usar “system” para rotinas).
- Todos timestamps em **UTC**.
- Invariante de consistência:
  - `Enrollment.state` deve coincidir com o `to_state` da última transição (quando houver transições).

## Plano de Implementação
- Modelar tabelas `Enrollment` e `EnrollmentTransition` com constraints e índices.
- Implementar repository transacional (get_by_id + save).
- Traduzir erros do DB em erros de infra.
- Criar testes de integração (round-trip, retry, concorrência, rollback).

## Checklist de Implementação
- [x] Modelar `Enrollment` (snapshot) com `version` e timestamps (`created_at`, `updated_at`, `*_at`)
- [x] Criar constraints de coerência por estado (timestamps obrigatórios/proibidos)
- [x] Criar índices: `state`, `student_id`, e compostos conforme consulta
- [ ] Modelar `EnrollmentTransition` (append-only)
- [x] Garantir `transition_id` unique (ADR 002)
- [x] Garantir `actor_id` obrigatório
- [x] Definir FK `enrollment_id` com ON DELETE PROTECT
- [x] Implementar `get_by_id` (snapshot + transitions) com reidratação segura
- [x] Implementar `save` transacional (snapshot + novas transitions)
- [x] Aplicar controle otimista por `version`
- [ ] Implementar tradução de erros de DB (unique, FK, concorrência)

## Checklist de Code Review
- [ ] O domínio não depende de ORM/DB
- [ ] O log é realmente append-only (sem update/delete)
- [ ] `save` insere apenas transitions novas
- [ ] `save` é atômico (ou tudo persiste, ou nada)
- [ ] Eventos só são publicados após commit (via pull na Application)
- [ ] Concorrência otimista está coberta por testes

## Checklist de Testes
- [ ] Persistir → reidratar → objetos equivalentes (round-trip)
- [ ] No-op não cria transition
- [ ] Retry não duplica transition (unique transition_id)
- [ ] Conflito de versão falha corretamente
- [ ] Rollback mantém snapshot/log consistentes