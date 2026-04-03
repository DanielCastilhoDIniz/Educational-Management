# Politica - Timestamps e UTC

## Objetivo
Padronizar o tratamento de tempo entre dominio, Application, persistencia e interface.

## Regras Sugeridas
- persistencia sempre em UTC
- datetimes sem timezone devem ser normalizados explicitamente
- `occurred_at` fornecido externamente deve passar por validacao e normalizacao
- o sistema deve definir quando aceita timestamp do cliente e quando usa o relogio do servidor
- logs e auditoria devem carregar timezone consistente

## Campos Relevantes
- `created_at`
- `updated_at`
- `occurred_at`
- `concluded_at`
- `cancelled_at`
- `suspended_at`
- `reactivated_at`

## Testes Recomendados
- entrada naive convertida corretamente
- entrada aware em fuso diferente convertida para UTC
- round-trip de persistencia preserva instante correto
- ordenacao cronologica do log continua deterministica
