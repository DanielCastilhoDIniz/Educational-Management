# API - Presenters, Serializacao e Versionamento

## Objetivo
Documentar como a API deve transformar resultados internos em payloads HTTP estaveis ao longo do tempo.

## Regras
- presenters HTTP devem ser centralizados por contexto ou por familia de respostas
- serializacao nao deve depender diretamente de classes do dominio
- versionamento de payload deve ser considerado quando a API deixar de ser interna
- responses devem privilegiar contratos estaveis e legiveis sobre espelhamento de estrutura interna

## Recomendacoes
- mapear `ApplicationResult` de commands para envelopes consistentes
- mapear queries/read models para DTOs de resposta dedicados
- padronizar datas, enums, status e identificadores
- evitar expor internals como `version` sem criterio funcional claro

## Quando Versionar
- mudanca breaking de campo
- mudanca de semantica do payload
- mudanca forte de filtros ou ordenacao em relatorios publicos
