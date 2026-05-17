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

## Checklist de Implementacao
- [ ] Widgets e consultas do painel do estudante foram definidos
- [ ] Existe dicionario de metricas academicas oficial
- [ ] Filtros por periodo, disciplina e data estao padronizados
- [ ] Dados parciais e oficiais sao sinalizados no contrato do painel
- [ ] Regras de visibilidade para estudante e responsavel foram formalizadas

## Checklist de Code Review
- [ ] O frontend nao recalcula regra de negocio critica do painel
- [ ] Metricas exibidas usam definicao unica entre painel, boletim e relatorios
- [ ] Nao ha vazamento de dados entre estudantes/responsaveis
- [ ] Freshness/cache do painel esta documentado

## Checklist de Testes
- [ ] Existem testes de agregacao por disciplina, periodo e data
- [ ] Existem testes de visibilidade para responsavel vinculado
- [ ] Existem testes para diferenciacao entre dado parcial e oficial
- [ ] Existem testes de consistencia entre painel e fontes academicas

## Checklist de Documentacao
- [ ] Especificacao oficial do painel do estudante foi publicada
- [ ] UX funcional e contratos de API do painel estao alinhados
- [ ] Dicionario de metricas e read models referenciam a mesma definicao

