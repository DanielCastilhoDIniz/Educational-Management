# ADR 019 - Multi-Tenancy e Isolamento por Instituicao

## Status
Proposto

## Contexto
O produto e um SaaS escolar, portanto precisa suportar multiplas instituicoes com configuracoes proprias e isolamento rigoroso de dados.

## Decisao
Adotar isolamento logico por tenant institucional como regra minima de arquitetura.

## Escopo do Produto e Modelo de Isolamento
- Fase 1 (atual): escolas de educacao basica e cursos temporarios — isolamento logico (banco compartilhado, schema compartilhado, filtrado por `tenant_id`)
- Fase 2 (futura): universidades e faculdades — isolamento fisico por schema ou banco dedicado quando compliance exigir
- O aggregate `User` e uma identidade global no banco — uma instituicao so enxerga um `User` se existe um `Membership` vinculando os dois; sem `Membership`, o `User` e invisivel para aquela instituicao
- Agrupamento de unidades em redes educacionais e resolvido no contexto Organizacional, nao no aggregate `User`

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

## Checklist de Implementacao
- [x] `institution_id` ja existe no aggregate `Enrollment`
- [ ] Comandos e consultas exigem contexto institucional explicito em toda a cadeia
- [ ] Repositorios e queries filtram por tenant de forma consistente
- [ ] Indices e constraints relevantes consideram o escopo do tenant
- [ ] Logs, metricas e auditoria preservam `tenant_id`/escopo institucional

## Checklist de Code Review
- [ ] Nao existem consultas cross-tenant por padrao
- [ ] A borda resolve tenant antes de chamar a Application
- [ ] Politicas configuraveis resolvem por tenant e escopo correto
- [ ] Acesso cross-tenant so ocorre por contrato explicito e auditavel

## Checklist de Testes
- [ ] Existem testes de isolamento entre tenants em comandos e consultas
- [ ] Existem testes garantindo negacao de acesso entre instituicoes
- [ ] Existem testes para chaves de negocio repetidas em tenants diferentes quando permitido
- [ ] Existem testes de auditoria com escopo institucional preservado

## Checklist de Documentacao
- [ ] A API documenta a resolucao de tenant e o contexto institucional
- [ ] O ADR 030 esta alinhado com este ADR sobre hierarquia organizacional
- [ ] Casos de uso deixam explicito o escopo institucional quando aplicavel

