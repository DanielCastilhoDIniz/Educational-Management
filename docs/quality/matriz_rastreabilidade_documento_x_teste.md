# Matriz de Rastreabilidade - Documento x Teste

## Objetivo
Ligar contratos documentados a suites de teste existentes ou planejadas.

## Estrutura Recomendada
- documento
- tipo (`ADR`, `use case`, `policy`, `checklist`)
- suite de teste relacionada
- status (`coberto`, `parcial`, `nao coberto`)
- observacoes

## Exemplos Iniciais
- ADR 008 -> testes de repositorio e round-trip
- ADR 009 -> testes do contrato de `save()`
- ADR 013 -> testes de traducao de erros
- use case de suspender matricula -> testes de Application e dominio
- politica de timestamps -> testes de normalizacao e persistencia

## Recomendacao
Toda nova decisao arquitetural que altere contrato deve indicar como sera validada por teste automatizado.
