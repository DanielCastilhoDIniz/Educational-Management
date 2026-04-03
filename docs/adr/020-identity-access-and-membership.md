# ADR 020 - Identidade, Acesso e Membership Institucional

## Status
Proposto

## Contexto
Usuarios poderao atuar como administrador, secretaria, professor, responsavel e outros papeis, possivelmente em mais de uma instituicao.

## Decisao
Separar identidade global de membership institucional.

## Regras
- `Usuario` representa identidade global da pessoa/conta
- `Membership` representa o vinculo do usuario a uma instituicao
- papeis e escopos pertencem ao membership, nao ao usuario global
- o mesmo usuario pode exercer papeis distintos em tenants diferentes
- service accounts devem ser modeladas explicitamente

## Consequencias
- melhora seguranca e flexibilidade multi-tenant
- evita duplicacao de usuarios por instituicao
- exige matriz de autorizacao por caso de uso

## Plano de Implementacao
- definir contrato de membership
- documentar papeis padrao e escopos
- criar politicas de autorizacao por contexto
