# Glossário

Glossário do contexto `academic.enrollment`.

Este documento registra a linguagem ubíqua usada no módulo de matrícula e ajuda a manter coerência entre:

- domínio
- application
- infrastructure
- testes
- documentação

## Identidade e rastreabilidade

### `aggregate_id`

- Camada: `application` / `domain`
- Significado: identificador do aggregate afetado pelo caso de uso.
- Uso: `ApplicationResult`, `ApplicationError`, eventos e rastreabilidade.
- No contexto atual: corresponde a `Enrollment.id`.

### `enrollment_id`

- Camada: `application`
- Significado: identificador usado como entrada do caso de uso para localizar uma matrícula.
- Uso: parâmetros de `cancel`, `suspend` e `conclude`.
- Observação: depois do load, representa o mesmo aggregate identificado por `aggregate_id`.

### `id`

- Camada: `domain`
- Significado: identidade do aggregate ou entidade.
- Uso: `Enrollment.id`.

### `actor_id`

- Camada: `domain` / `application`
- Significado: identificador de quem executou a ação.
- Uso: auditoria, transições e eventos de domínio.
- Exemplos: usuário, sistema, processo agendado.

### `event_id`

- Camada: `domain`
- Significado: identificador único do evento de domínio.
- Uso: rastreabilidade de eventos.
- Observação: hoje os eventos usam `uuid4`.

### `transition_id`

- Camada: `infrastructure`
- Significado: identificador determinístico de uma transição persistida.
- Uso: deduplicação de retries no log append-only.
- Referência: ADR `002`.

## Aggregate e objetos centrais

### `Enrollment`

- Camada: `domain`
- Significado: aggregate root do contexto de matrícula.
- Responsabilidades: validar invariantes internas, executar transições válidas e acumular eventos de domínio.

### `StateTransition`

- Camada: `domain`
- Significado: value object que representa uma transição de estado.
- Campos centrais: `from_state`, `to_state`, `actor_id`, `occurred_at`, `justification`.
- Uso: histórico da matrícula e auditoria interna.

### `ConclusionVerdict`

- Camada: `domain`
- Significado: value object que representa a decisão de permitir ou bloquear a conclusão.
- Campos centrais: `is_allowed`, `reasons`, `requires_justification`.
- Regra atual: `reasons` é imutável e armazenado como `tuple[str, ...]`.

### `DomainEvent`

- Camada: `domain`
- Significado: fato imutável ocorrido no negócio.
- Uso: registro de mudanças relevantes após transições válidas.
- Regra: o domínio cria eventos, mas não publica eventos externamente.

## Estados e transições

### `state`

- Camada: `domain`
- Significado: estado atual da matrícula.
- Uso: base das invariantes e das transições permitidas.

### `current_state`

- Camada: `domain` / `application`
- Significado: estado em que o aggregate se encontra no momento da tentativa.
- Uso: `details` de erro, rastreabilidade e mapeamento para `ApplicationError`.

### `new_state`

- Camada: `application`
- Significado: estado final após uma mudança bem-sucedida.
- Uso: retorno de `ApplicationResult` quando `changed=True`.

### `from_state`

- Camada: `domain`
- Significado: estado anterior de uma transição ou evento.

### `to_state`

- Camada: `domain`
- Significado: estado resultante de uma transição ou evento.

### `EnrollmentState`

- Camada: `domain`
- Significado: enum técnico dos estados da matrícula.
- Valores atuais:
  - `ACTIVE = "active"`
  - `SUSPENDED = "suspended"`
  - `CONCLUDED = "concluded"`
  - `CANCELLED = "cancelled"`

### Mapeamento PT-BR -> enum técnico

- `ATIVA` -> `ACTIVE`
- `TRANCADA` -> `SUSPENDED`
- `CONCLUÍDA` -> `CONCLUDED`
- `CANCELADA` -> `CANCELLED`

Referência: ADR `003`.

## Temporalidade

### `created_at`

- Camada: `domain` / `infrastructure`
- Significado: momento de criação técnica da matrícula.

### `updated_at`

- Camada: `infrastructure`
- Significado: momento da última atualização do snapshot persistido.

### `occurred_at`

- Camada: `domain`
- Significado: momento em que a ação aconteceu no mundo de negócio.
- Uso: transições e eventos.
- Regra: deve ser normalizado para UTC.

### `concluded_at`

- Camada: `domain`
- Significado: timestamp da conclusão.
- Invariante: obrigatório quando `state == CONCLUDED`.

### `cancelled_at`

- Camada: `domain`
- Significado: timestamp do cancelamento.
- Invariante: obrigatório quando `state == CANCELLED`.

### `suspended_at`

- Camada: `domain`
- Significado: timestamp da suspensão.
- Invariante: obrigatório quando `state == SUSPENDED`.

## Fluxo de eventos

### `domain_events`

- Camada: `application`
- Significado: snapshot imutável dos eventos pendentes do aggregate retornado pelo caso de uso.
- Uso: `ApplicationResult`.
- Regra: quando `changed=True`, `domain_events` não pode ser vazio.

### `peek_domain_events()`

- Camada: `domain`
- Significado: leitura não destrutiva do buffer de eventos do aggregate.
- Uso: a `application` usa isso para capturar o snapshot antes do `save`.

### `pull_domain_events()`

- Camada: `domain`
- Significado: extração destrutiva dos eventos pendentes.
- Uso: limpar o buffer após persistência bem-sucedida.

### Event buffer

- Camada: `domain`
- Significado: lista interna de eventos pendentes acumulados pelo aggregate.
- Regra: não deve ser drenado antes da persistência.
- Referência: ADR `005`.

## Contrato da Application

### `ApplicationResult`

- Camada: `application`
- Significado: contrato estável de saída dos casos de uso.
- Campos centrais:
  - `aggregate_id`
  - `success`
  - `changed`
  - `domain_events`
  - `new_state`
  - `error`

### `success`

- Camada: `application`
- Significado: indica se o caso de uso terminou sem falha esperada.

### `changed`

- Camada: `application`
- Significado: indica se houve mudança real de estado.
- Regra:
  - `changed=True` implica `domain_events` não vazio e `new_state` preenchido
  - `changed=False` implica ausência de mudança efetiva

### `ApplicationError`

- Camada: `application`
- Significado: payload estável e serializável de falha esperada.
- Uso: retorno de `ApplicationResult(success=False)`.

### `ErrorCodes`

- Camada: `application`
- Significado: códigos estáveis de máquina para falhas esperadas.
- Valores atuais:
  - `ENROLLMENT_NOT_FOUND`
  - `JUSTIFICATION_REQUIRED`
  - `UNEXPECTED_ERROR`
  - `INVALID_STATE_TRANSITION`
  - `ENROLLMENT_NOT_ACTIVE`
  - `CONCLUSION_NOT_ALLOWED`
  - `STATE_INTEGRITY_VIOLATION`
  - `CONCURRENCY_CONFLICT`
  - `DATA_INTEGRITY_ERROR`

## Erros e diagnóstico

### `code`

- Camada: `domain` / `application`
- Significado: identificador estável do erro.

### `message`

- Camada: `domain` / `application`
- Significado: descrição humana do problema.

### `details`

- Camada: `domain` / `application`
- Significado: metadados estruturados para diagnóstico e rastreabilidade.

### `attempted_action`

- Camada: `domain`
- Significado: ação tentada pelo ator.
- Exemplos: `cancel`, `suspend`, `conclude`, `reactivate`.

### `required_state`

- Camada: `domain`
- Significado: estado necessário para a ação ser válida.

### `allowed_from_states`

- Camada: `domain`
- Significado: lista de estados aceitos como origem da transição.

### `domain_code`

- Camada: `application`
- Significado: código original do erro de domínio preservado no `details` do `ApplicationError`.

### `STATE_INTEGRITY_VIOLATION`

- Camada: `application`
- Significado: inconsistência entre estado, eventos ou contrato interno do fluxo.
- Exemplos:
  - evento sem mudança de estado
  - mudança de estado sem evento
  - fallback de erro de domínio não mapeado

## Persistência e infraestrutura

### Snapshot

- Camada: `infrastructure`
- Significado: representação persistida do estado atual da matrícula.
- No projeto: `EnrollmentModel`.

### Transition log

- Camada: `infrastructure`
- Significado: histórico append-only das transições persistidas.
- No projeto: `EnrollmentTransitionModel`.

### `version`

- Camada: `domain` / `infrastructure`
- Significado: versão do snapshot usada para concorrência otimista.
- Estado atual: o campo existe; a aplicação completa da concorrência ainda está pendente.

### `EnrollmentRepository`

- Camada: `application`
- Significado: port de persistência usado pelos casos de uso.
- Operações atuais: `get_by_id` e `save`.

## Termos preferidos

Use estes termos no projeto:

- `domain_events`, não `events`, no contrato da `application`
- `aggregate_id`, não `entity_id`, quando o contexto for o aggregate
- `EnrollmentState`, não strings soltas de estado no core
- `ApplicationResult`, não exceção, como contrato esperado da camada de `application`
- `ApplicationError`, não `Exception`, para falhas previstas

## Referências

- `DOMIAIN_ROLES.md`
- `README.md`
- `docs/adr/001-enrollment-persistence.md`
- `docs/adr/003-Ubiquitous-languagePTbr.md`
- `docs/adr/005-Domain-eventes.md`
- `docs/adr/007-domain-layer-core.md`
- `docs/adr/008-application-layer-use-case-orchestration.md`
- `docs/adr/009-infrastructure-layer-adapters-persistence-publication.md`
- `docs/adr/010-interface-http-boundary.md`

