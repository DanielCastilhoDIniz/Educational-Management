# Guia de Migracoes e Evolucao de Schema

## Objetivo
Padronizar como o projeto deve tratar mudancas de schema e seus impactos arquiteturais e operacionais.

## Regras Sugeridas
- migracao relevante deve considerar impacto em leitura, reporting e exportacao
- read models derivados devem ser avaliados quando schema mudar
- mudanca breaking em dado oficial exige plano de rollout e rollback
- constraints devem ser preferidas quando reforcam contrato de negocio ou integridade
- migracoes destrutivas exigem documentacao e avaliacao operacional mais forte

## Perguntas Antes de Aplicar
- impacta boletim, dashboard ou relatorio
- exige backfill
- muda contrato de query
- exige janela de manutencao
- precisa de estrategia de compatibilidade temporaria
