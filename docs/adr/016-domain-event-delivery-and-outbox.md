# ADR 016 - Entrega de Eventos de Dominio e Outbox

## Status
Proposto

## Contexto
O modulo ja registra eventos de dominio no aggregate e preserva o buffer ate a persistencia bem-sucedida. Falta formalizar a estrategia de entrega externa resiliente quando o projeto ganhar integracoes reais.

## Decisao
Adotar outbox transacional como estrategia alvo para entrega externa de eventos do modulo.

## Regras
1. O aggregate continua registrando eventos em memoria.
2. A Application continua coordenando persistencia antes do consumo definitivo do buffer.
3. Quando houver integracao externa, os eventos devem ser gravados em outbox na mesma transacao do snapshot/log.
4. A entrega para barramento, fila ou webhook deve ocorrer fora da transacao principal.
5. Consumidores devem ser idempotentes.

## Consequencias

### Positivas
- reduz risco de perder evento apos commit
- desacopla persistencia de entrega externa
- facilita retries e operacao em producao

### Negativas / Riscos
- aumenta a quantidade de componentes operacionais
- exige monitoramento de fila pendente e dead letter

## Invariantes
- nao publicar evento externo antes do commit
- nao perder evento confirmado por falha entre commit e publish
- manter rastreabilidade entre aggregate, transition e outbox record

## Plano de Implementacao
- definir schema da outbox
- definir envelope do evento
- decidir politica de retry e dead letter
- criar worker de entrega e dashboards operacionais
