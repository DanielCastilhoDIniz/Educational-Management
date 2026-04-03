# Politica - Multi-Tenancy e Isolamento Institucional

## Objetivo
Garantir que cada instituicao opere como tenant isolado do ponto de vista de dados, autorizacao e auditoria.

## Regras Sugeridas
- toda entidade operacional deve carregar contexto institucional explicito
- consultas sem filtro de tenant sao proibidas em codigo de negocio
- usuarios acessam dados apenas de tenants em que possuem membership valido
- logs e trilhas de auditoria devem incluir `tenant_id`
- exportacoes e relatorios devem ser tenant-scoped

## Testes Recomendados
- usuario de tenant A nao enxerga tenant B
- consulta sem tenant falha cedo
- auditoria preserva tenant em eventos e logs
