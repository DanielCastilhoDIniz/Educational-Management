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
