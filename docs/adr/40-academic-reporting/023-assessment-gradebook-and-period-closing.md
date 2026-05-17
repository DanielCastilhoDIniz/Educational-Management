# ADR 023 - Avaliacoes, Notas, Medias e Fechamento de Periodo

## Status
Proposto

## Contexto
Instituicoes podem escolher a quantidade de avaliacoes por periodo, formulas de media e regras de recuperacao. O produto precisa suportar essa variacao sem hardcode fragil.

## Decisao
Adotar regime avaliativo configuravel por instituicao e periodo, consumido pela Application e contextos especializados.

## Regras
- quantidade de avaliacoes por periodo nao deve ser fixa no codigo
- formula de media deve ser configuravel e auditavel
- notas devem ser vinculadas a avaliacao explicita
- fechamento de periodo deve consolidar resultado com base nas politicas congeladas naquele periodo
- alteracoes apos fechamento exigem fluxo de retificacao documentado

## Consequencias
- maior aderencia ao mundo real escolar
- exige modelagem forte de politicas e consolidacao
- aumenta importancia de auditoria e congelamento por periodo

## Plano de Implementacao
- definir catalogo de politicas avaliativas
- modelar avaliacao, nota e consolidado
- documentar fluxo de fechamento de periodo e retificacao

## Checklist de Implementacao
- [ ] Existe modelo de avaliacao, nota e consolidado por periodo
- [ ] Quantidade de avaliacoes por periodo nao e fixa no codigo
- [ ] Formula de media e configuravel e auditavel
- [ ] Fechamento de periodo congela politicas aplicadas
- [ ] Retificacao apos fechamento possui fluxo proprio

## Checklist de Code Review
- [ ] Regras de media nao ficam escondidas em interface ou planilha improvisada
- [ ] Politicas congeladas de periodo sao respeitadas pelo consolidado
- [ ] Alteracoes apos fechamento deixam trilha auditavel
- [ ] Relatorios oficiais usam apenas resultados consolidados

## Checklist de Testes
- [ ] Existem testes para diferentes formulas de media
- [ ] Existem testes para quantidades variaveis de avaliacoes
- [ ] Existem testes de fechamento de periodo e consolidacao
- [ ] Existem testes de retificacao apos fechamento

## Checklist de Documentacao
- [ ] Politica de regime avaliativo foi oficializada
- [ ] Casos de uso de lancar notas e fechar periodo estao alinhados ao ADR
- [ ] Boletim e registros oficiais referenciam a mesma base conceitual

