# ADR 024 - Estudantes, Responsaveis e Dados de Contato

## Status
Proposto

## Contexto
O SaaS precisa manter dados de estudantes, seus responsaveis e contatos, com impacto em comunicacao, autorizacao e operacao escolar.

## Decisao
Separar dados cadastrais da pessoa, relacionamentos de responsabilidade e preferencias de contato.

## Regras
- estudante e responsavel devem ser entidades conceituais distintas
- um estudante pode ter mais de um responsavel
- um responsavel pode estar vinculado a mais de um estudante
- relacao deve informar tipo de responsabilidade e prioridade de contato quando necessario
- dados sensiveis e contatos exigem politica de privacidade e auditoria

## Consequencias
- melhora flexibilidade do cadastro escolar
- evita duplicar pessoa para cada vinculo
- exige politicas claras de consentimento e visibilidade

## Plano de Implementacao
- definir modelo de pessoa/contato/responsabilidade
- documentar regras de unicidade e merge de cadastro
- definir politicas de acesso a dados sensiveis
