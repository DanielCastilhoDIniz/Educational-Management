# ADR 025 - Boletim, Historicos e Registros Oficiais

## Status
Proposto

## Contexto
O produto tende a evoluir para emitir boletins, historicos e outros registros que dependem de dados consolidados e auditaveis.

## Decisao
Tratar relatorios oficiais como derivados de dados consolidados, nunca como fonte primaria de verdade.

## Regras
- boletim deve derivar de notas, frequencia e consolidado de periodo
- historico deve derivar de matriculas concluidas e resultados consolidados
- documentos oficiais devem carregar rastreabilidade de versao e data de emissao
- retificacoes devem preservar trilha de auditoria

## Consequencias
- reduz divergencia entre operacao e documento emitido
- exige contratos fortes de fechamento e consolidacao

## Plano de Implementacao
- definir quais documentos oficiais o produto suportara
- documentar dependencias de dados e politicas de emissao
- incluir trilha de auditoria de geracao e retificacao

## Checklist de Implementacao
- [ ] O catalogo de documentos oficiais suportados esta definido
- [ ] Emissao usa dados consolidados como fonte de verdade
- [ ] Documentos carregam versao, data/hora e rastreabilidade de emissao
- [ ] Fluxo de retificacao preserva historico auditavel
- [ ] Permissoes de emissao e reemissao estao formalizadas

## Checklist de Code Review
- [ ] Boletim/historico nao viram fonte primaria de verdade
- [ ] Documento oficial e dado parcial sao diferenciados claramente
- [ ] Emissao so ocorre sobre dados fechados/consolidados quando exigido
- [ ] Retificacoes nao apagam historico anterior

## Checklist de Testes
- [ ] Existem testes de emissao de boletim a partir de dados consolidados
- [ ] Existem testes de historico derivado de matriculas concluidas
- [ ] Existem testes de versao/data de emissao
- [ ] Existem testes de retificacao com trilha auditavel

## Checklist de Documentacao
- [ ] Politica de emissao e versao oficial foi oficializada
- [ ] Catalogo de relatorios e documentos esta alinhado ao ADR
- [ ] Casos de uso de boletim e reporting referenciam a mesma base oficial

