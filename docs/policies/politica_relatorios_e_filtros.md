# Politica - Relatorios, Filtros e Exportacoes

## Objetivo
Padronizar como filtros, ordenacao e exportacoes devem se comportar em relatorios operacionais e analiticos.

## Regras Sugeridas
- filtros comuns devem ser consistentes entre relatorios do mesmo dominio
- relatorio em tela e exportacao devem usar o mesmo criterio de selecao
- toda exportacao deve carregar metadados dos filtros aplicados
- relatorios devem identificar se o dado e parcial ou oficial
- filtros invalidos devem falhar com contrato estavel e mensagem clara

## Testes Recomendados
- exportacao igual ao resultado filtrado em tela
- filtro invalido rejeitado
- ordenacao consistente
- paginacao consistente com total informado
