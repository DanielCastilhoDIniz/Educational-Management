# ADR 026 - Reporting, Read Models e Contratos de Consulta

## Status
Proposto

## Contexto
Relatorios, boletins e dashboards exigem consultas agregadas, filtros compostos e desempenho previsivel. Esses cenarios normalmente nao combinam com o mesmo modelo transacional usado para comandos.

## Decisao
Adotar read models e contratos de consulta especificos para reporting e analytics, sem transformar relatorios em fonte primaria de verdade.

## Regras
- relatorios leem de modelos otimizados para consulta, quando necessario
- dados oficiais devem continuar derivando de fontes transacionais consolidadas
- consultas de relatorio devem ser read-only
- contratos de consulta devem explicitar filtros, ordenacao, paginacao e data de referencia
- resultados devem informar se sao parciais ou oficiais

## Consequencias
- melhora performance e clareza do contrato de leitura
- reduz acoplamento entre telas analiticas e aggregates transacionais
- exige estrategia de atualizacao e rastreabilidade dos read models

## Plano de Implementacao
- catalogar consultas de reporting prioritarias
- decidir quais usam leitura direta e quais exigem read model dedicado
- documentar freshness e consistencia esperadas por saida

## Checklist de Implementacao
- [ ] Consultas prioritarias de reporting foram catalogadas
- [ ] Read models dedicados foram identificados quando necessarios
- [ ] Contratos de consulta explicam filtros, ordenacao, paginacao e data de referencia
- [ ] Estrategia de atualizacao/freshness dos read models foi definida
- [ ] Resultados indicam se sao parciais ou oficiais

## Checklist de Code Review
- [ ] Read models permanecem read-only
- [ ] Consultas pesadas nao sobrecarregam aggregates transacionais sem necessidade
- [ ] Freshness/consistencia e explicita para cada saida
- [ ] Dados oficiais continuam derivados das fontes transacionais consolidadas

## Checklist de Testes
- [ ] Existem testes de contrato de query
- [ ] Existem testes de filtros, ordenacao e paginacao
- [ ] Existem testes de consistencia entre read model e fonte transacional
- [ ] Existem testes de indicacao de dado parcial/oficial

## Checklist de Documentacao
- [ ] Catalogo de read models foi oficializado
- [ ] Casos de uso de relatorio e dashboard apontam para contratos de consulta corretos
- [ ] Documentacao de freshness e consistencia esta alinhada ao ADR

