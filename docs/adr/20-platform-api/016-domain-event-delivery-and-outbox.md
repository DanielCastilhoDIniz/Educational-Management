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

## Checklist de Implementacao
- [x] O aggregate continua registrando eventos em memoria
- [x] A Application persiste antes de drenar o buffer de eventos
- [ ] Existe outbox persistido na mesma transacao do dado transacional
- [ ] Existe dispatcher de entrega com retry e monitoramento
- [ ] Eventos externos possuem chave de idempotencia/versionamento definida

## Checklist de Code Review
- [x] Nenhuma entrega externa ocorre antes do commit
- [ ] Publicadores consomem apenas eventos extraidos, sem criar eventos na infra
- [ ] Reentregas nao produzem efeitos duplicados em consumidores
- [ ] Falhas de entrega nao quebram a consistencia do dado principal

## Checklist de Testes
- [x] Existem testes garantindo persistencia antes do `pull`
- [ ] Existem testes de escrita no outbox na mesma transacao
- [ ] Existem testes de retry/reativacao de entrega externa
- [ ] Existem testes de idempotencia do consumo ou da entrega

## Checklist de Documentacao
- [ ] Catalogo de eventos descreve payload, origem e destino
- [ ] Runbook operacional cobre fila pendente, retry e falha de entrega
- [ ] Politica de versionamento de eventos esta documentada

