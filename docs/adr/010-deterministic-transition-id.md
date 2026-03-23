# ADR 010 - Deterministic Transition ID (UUIDv5)

## Status
Aprovado

## Contexto
Transicoes de estado da matricula sao persistidas como log append-only. Em cenarios reais de retry, falhas transitorias e reprocessamento, precisamos impedir duplicacao do mesmo fato logico no log.

Se o ID fosse aleatorio (`uuid4`), retries gerariam IDs diferentes e o banco aceitaria duplicatas.

## Decisao
Gerar `transition_id` de forma deterministica usando `UUIDv5`, a partir de:

- um namespace UUID fixo do bounded context
- um fingerprint canonico da transicao

O dominio nao gera `transition_id`; isso pertence a persistencia.

## Consequencias

### Positivas
- idempotencia no nivel do banco
- retries seguros
- auditoria consistente
- dominio permanece puro

### Negativas / Riscos
- o namespace nao pode mudar
- o fingerprint deve permanecer estavel
- exige normalizacao rigorosa de timestamps e campos opcionais

## Regras e Invariantes

### Namespace
- constante unica por bounded context: `ACADEMIC_ENROLLMENT_TRANSITION_NS`
- gerado uma unica vez, hardcoded e imutavel

### Fingerprint
Composicao minima:

- `enrollment_id`
- `action`
- `from_state`
- `to_state`
- `occurred_at` em ISO 8601 UTC
- `actor_id`
- `justification` normalizada (`None -> ""`, trim)

Formato estavel:

`enrollment:<id>|action:<action>|from:<from>|to:<to>|at:<iso_utc>|actor:<actor>|just:<just>`

## Plano de Implementacao
- criar helper unico na infra para normalizacao + geracao UUIDv5
- garantir que todo insert de transition passe por esse helper
- tratar unique violation como retry idempotente quando o snapshot estiver consistente

## Checklist de Implementacao
- [x] Definir `ACADEMIC_ENROLLMENT_TRANSITION_NS` como constante hardcoded
- [x] Criar helper unico para:
  - [x] normalizar `occurred_at` para UTC timezone-aware
  - [x] normalizar `justification` (`None -> ""`, trim)
  - [x] construir fingerprint estavel
  - [x] gerar `UUIDv5(namespace, fingerprint)`
- [ ] Garantir uso obrigatorio do helper em todo insert de transition
- [x] Definir `transition_id` unique no DB

## Checklist de Code Review
- [x] Namespace e constante e nao muda entre deploys
- [x] Fingerprint nao depende de campos volateis (`updated_at`, `version`)
- [x] `occurred_at` e sempre UTC antes do fingerprint
- [ ] `action` e deterministica (mesma intencao -> mesma action)
- [ ] Unique violation e tratada de forma idempotente

## Checklist de Testes
- [ ] Mesmo input gera mesmo `transition_id` (determinismo)
- [ ] Retry nao duplica transition (unique)
- [ ] Campos opcionais normalizados nao mudam o ID indevidamente
- [ ] `occurred_at` com timezone diferente normaliza e gera ID esperado
