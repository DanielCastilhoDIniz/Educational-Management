# API - Autenticacao, Membership e Contexto de Tenant

## Objetivo
Documentar como a camada HTTP deve resolver identidade, membership e tenant antes de delegar para a Application.

## Regras
- toda request autenticada deve resolver `user_id`
- toda request tenant-scoped deve resolver `institution_id` ou `tenant_id`
- o papel e os escopos do ator devem vir do membership institucional
- a Application nao deve depender de detalhes do token HTTP
- a borda deve traduzir o contexto autenticado para um objeto/DTO de ator e tenant

## Fontes de Contexto Possiveis
- token JWT
- sessao autenticada
- API key de integracao
- service account institucional

## Campos Minimos do Contexto Resolvido
- `actor_id`
- `actor_type`
- `tenant_id`
- `membership_id`, quando aplicavel
- papeis e escopos relevantes
- `correlation_id`

## Falhas Esperadas na Borda
- nao autenticado
- tenant ausente
- membership ausente
- token valido mas sem escopo suficiente

## Recomendacao
Autenticacao e autorizacao de transporte devem falhar cedo, antes de chamar a Application, mas sem replicar regra de negocio do caso de uso.
