# ADR 028 - Painel do Estudante e Agregacao de Metricas Academicas

## Status
Proposto

## Contexto
O painel do estudante combina frequencia, desempenho por disciplina, periodo e recorte temporal. Ele nao e apenas uma tela, mas uma agregacao de metricas com regras de visibilidade e atualizacao.

## Decisao
Tratar o painel do estudante como surface de leitura propria, sustentada por metricas academicas definidas e contratos de visibilidade explicitos.

## Regras
- painel do estudante nao recalcula regras de negocio no frontend
- metricas exibidas devem ter definicao documental unica
- filtros por periodo, disciplina e data devem ser suportados de forma consistente
- dados parciais e oficiais devem ser identificados claramente
- responsavel so pode ver estudantes a ele vinculados

## Consequencias
- melhora consistencia entre portal do estudante, boletim e relatorios
- exige dicionario de metricas e contrato de visibilidade
- prepara o caminho para analytics sem misturar regra no cliente

## Plano de Implementacao
- definir widgets e consultas do painel
- definir metrica oficial x metrica parcial
- documentar cache, freshness e trilha de auditoria quando aplicavel
