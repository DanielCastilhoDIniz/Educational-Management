# Guia de Quando Abrir ADR

## Objetivo
Evitar tanto o excesso quanto a falta de ADRs, abrindo decisao formal quando isso realmente protege o projeto.

## Abrir ADR Quando
- a decisao muda fronteira entre camadas
- a decisao altera contrato entre contextos
- a decisao impacta multiplos modulos
- a decisao cria um padrao duradouro de implementacao
- a decisao muda tecnologia base ou estrategia de persistencia, integracao, API ou auth

## Nao Abrir ADR Quando
- e apenas detalhe local de implementacao
- e ajuste cosmetico ou refactor interno sem impacto de contrato
- a mudanca e reversivel e isolada demais para exigir governanca formal

## Regra Pratica
Se a equipe puder discordar legitimamente e a decisao tiver impacto duradouro, vale considerar ADR.
