# ADR 020 - Identidade, Acesso e Membership Institucional

## Status
Proposto

## Contexto
Usuários poderão atuar como administrador, secretaria, professor, responsável e outros papeis, possivelmente em mais de uma instituição.

## Decisão
Separar identidade global de membership institucional.

## Regras
- `Usuario` representa identidade global da pessoa/conta
- `Membership` representa o vinculo do usuário a uma instituição
- papeis e escopos pertencem ao membership, nao ao usuário global
- o mesmo usuário pode exercer papeis distintos em tenants diferentes
- service accounts devem ser modeladas explicitamente

## Consequências
- melhora seguranca e flexibilidade multi-tenant
- evita duplicacao de usuarios por instituicao
- exige matriz de autorização por caso de uso

## Detalhamento
Esta decisao foi desdobrada em ADRs especificos:
- [ADR 031 - Design do Aggregate Membership](031-membership-aggregate-design.md) — campos, estados, `registration_code`, `MembershipTransition` e chave de negocio do `Membership`.
- [ADR 032 - Design do Aggregate User](032-user-aggregate-design.md) — campos, estados, `LegalIdentity`, `guardian_id`, `UserTransition` e relacao com Django auth.

## Plano de Implementacao
- definir contrato de membership
- documentar papeis padrão e escopos
- criar politicas de autorização por contexto

## Checklist de Implementação
- [ ] Existe separacao formal entre identidade global e membership institucional
- [ ] Papeis e escopos ficam no membership e nao no usuario global
- [ ] Service accounts sao modeladas explicitamente
- [ ] A borda traduz autenticacao em contexto de ator + membership
- [ ] Membership inativo pode bloquear uso de casos de uso

## Checklist de Code Review
- [ ] O mesmo usuario pode ter papeis diferentes em tenants diferentes
- [ ] Nenhum caso de uso autoriza apenas com `actor_id` cru
- [ ] Papeis globais nao substituem escopo institucional quando ele e obrigatorio
- [ ] Identidade, autorizacao e auditoria usam o mesmo modelo conceitual

## Checklist de Testes
- [ ] Existem testes de membership por tenant
- [ ] Existem testes de usuario com multiplos papeis em tenants distintos
- [ ] Existem testes de negacao para membership inativo ou ausente
- [ ] Existem testes de service account com escopo controlado

## Checklist de Documentacao
- [ ] Matriz ator x caso de uso x escopo foi promovida para a trilha oficial
- [ ] Guia de autenticacao/API reflete membership institucional
- [ ] Casos de uso administrativos documentam os papeis minimos necessarios

