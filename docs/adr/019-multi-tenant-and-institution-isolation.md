# ADR 019 - Multi-Tenancy e Isolamento por Instituicao

## Status
Proposto

## Contexto
O produto e um SaaS escolar, portanto precisa suportar multiplas instituicoes com configuracoes proprias e isolamento rigoroso de dados.

## Decisao
Adotar isolamento logico por tenant institucional como regra minima de arquitetura.

## Regras
- toda entidade de negocio relevante deve pertencer a uma instituicao ou escopo institucional claro
- consultas e comandos devem carregar contexto institucional explicito
- autorizacao depende de membership do usuario no tenant
- logs, metricas e auditoria devem preservar `tenant_id`
- politicas configuraveis devem resolver por tenant e, quando aplicavel, por unidade/periodo

## Consequencias
- reduz vazamento de dados entre clientes
- orienta contratos de repositorio e interface
- exige disciplina em indices, queries e auditoria

## Plano de Implementacao
- definir `tenant_id` nos contextos relevantes
- padronizar filtros por tenant na infra
- incluir isolamento multi-tenant nos checklists e testes
