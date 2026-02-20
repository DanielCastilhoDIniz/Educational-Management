# ADR 002 — Deterministic Transition ID (UUIDv5)

## Status
Aprovado

## Contexto
Transições de estado da matrícula são persistidas como log append-only.
Em cenários reais (retry de request, falhas transitórias, reprocessamento),
precisamos impedir duplicação do mesmo “fato lógico” no log.

Se o ID fosse aleatório (uuid4), retries gerariam IDs diferentes e o banco aceitaria duplicatas.

## Decisão
Gerar `transition_id` de forma **determinística** usando **UUIDv5**, a partir de:

- um **namespace UUID fixo** do bounded context
- um **fingerprint canônico** da transição

O domínio **não** gera `transition_id`. Essa é uma preocupação de persistência (infra).

## Consequências

### Positivas
- Idempotência no nível do banco.
- Retries seguros.
- Auditoria consistente (sem transições duplicadas).
- Domínio permanece puro (sem acoplamento a UUIDv5).

### Negativas / Riscos
- Namespace não pode mudar (quebra deduplicação histórica).
- Fingerprint deve permanecer estável (mudanças quebram determinismo).
- Exige normalização rigorosa de timestamps e campos opcionais.

## Regras e Invariantes

### Namespace (rígido)
- Constante única por bounded context:
  - `ACADEMIC_ENROLLMENT_TRANSITION_NS`
- Gerado uma única vez, hardcoded e **imutável**.

### Fingerprint (canônico e estável)
Composição mínima:
- `enrollment_id`
- `action` (determinística)
- `from_state`
- `to_state`
- `occurred_at` (ISO 8601 UTC, timezone-aware)
- `actor_id`
- `justification` normalizada (None → "", trim)

Formato estável:
enrollment:<id>|action:<action>|from:<from>|to:<to>|at:<iso_utc>|actor:<actor>|just:<just>

## Plano de Implementação
- Criar um único helper na infra para normalização + geração UUIDv5.
- Garantir que todos inserts de transitions passem por esse helper.
- Tratar unique violation como retry idempotente quando o snapshot estiver consistente.

## Checklist de Implementação
- [ ] Definir `ACADEMIC_ENROLLMENT_TRANSITION_NS` como constante hardcoded
- [ ] Criar helper único para:
  - [ ] normalizar `occurred_at` para UTC timezone-aware
  - [ ] normalizar `justification` (None → "", trim)
  - [ ] construir fingerprint estável
  - [ ] gerar UUIDv5(namespace, fingerprint)
- [ ] Garantir uso obrigatório do helper em todo insert de transition
- [ ] Definir `transition_id` unique no DB

## Checklist de Code Review
- [ ] Namespace é constante e não muda entre deploys
- [ ] Fingerprint não depende de campos voláteis (ex.: updated_at, version)
- [ ] `occurred_at` é sempre UTC antes do fingerprint
- [ ] `action` é determinística (mesma intenção → mesma action)
- [ ] Unique violation é tratada de forma idempotente (sem quebrar consistência)

## Checklist de Testes
- [ ] Mesmo input gera mesmo `transition_id` (determinismo)
- [ ] Retry não duplica transition (unique)
- [ ] Campos opcionais normalizados não mudam o ID indevidamente
- [ ] `occurred_at` com timezone diferente normaliza e gera ID esperado