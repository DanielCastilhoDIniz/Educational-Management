# ADR 018 - Observabilidade, Auditoria e Suporte Operacional

## Status
Proposto

## Contexto
Conforme o modulo crescer, erros de concorrencia, retries, politicas externas e publicacao de eventos vao exigir visibilidade operacional maior do que apenas stack trace e teste local.

## Decisao
Adotar requisitos minimos de observabilidade e auditoria desde o desenho dos casos de uso.

## Requisitos Minimos

### Logs Estruturados
Campos recomendados:
- `aggregate_id`
- `actor_id`
- `use_case`
- `action`
- `current_state`
- `new_state`
- `transition_id` quando houver
- `result`
- `error_code`
- `duration_ms`
- `correlation_id`

### Metricas
- taxa de sucesso por caso de uso
- taxa de no-op/idempotencia
- taxa de conflito de concorrencia
- taxa de erro tecnico
- tempo medio por operacao

### Auditoria
- trilha por matricula
- trilha por ator
- trilha por transicao
- justificativas preservadas

### Alertas
- aumento anormal de `CONCURRENCY_CONFLICT`
- fila de outbox envelhecida
- falhas repetidas de integridade

## Consequencias
- melhora diagnostico e suporte
- ajuda a provar comportamento correto em producao
- exige padronizacao desde cedo

## Plano de Implementacao
- padronizar campos de log por caso de uso
- definir metrica minima por adapter
- mapear consultas de auditoria necessarias para suporte
- incluir observabilidade no checklist de release

## Checklist de Implementacao
- [ ] Logs estruturados usam campos minimos por caso de uso
- [ ] `correlation_id` e propagado entre interface, application e infraestrutura
- [ ] Metricas minimas por caso de uso foram definidas e expostas
- [ ] Auditoria operacional distingue comando bem-sucedido, no-op e falha
- [ ] Existem alertas/runbooks para conflitos, retries e falhas de persistencia

## Checklist de Code Review
- [ ] Logs nao vazam dados sensiveis ou pessoais sem necessidade
- [ ] Codigos de erro aparecem de forma consistente em logs e auditoria
- [ ] Observabilidade nao depende de stack trace como fonte primaria
- [ ] Auditoria de negocio esta separada de log tecnico de debug

## Checklist de Testes
- [ ] Existem testes ou smoke checks para campos obrigatorios de log
- [ ] Existem testes para trilha de auditoria em mudancas de estado
- [ ] Existem testes para preservacao de `correlation_id` no fluxo
- [ ] Existem testes garantindo que dados sensiveis nao vazam indevidamente

## Checklist de Documentacao
- [ ] Runbooks operacionais cobrem incidentes principais do modulo
- [ ] Catalogo de metricas e logs esta documentado
- [ ] Requisitos nao funcionais de observabilidade estao alinhados

