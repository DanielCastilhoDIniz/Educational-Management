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

## Checklist de Implementacao
- [ ] Existe modelo separado para estudante, responsavel e contato
- [ ] Relacao estudante-responsavel suporta multiplos vinculos
- [ ] Tipo de responsabilidade e prioridade de contato foram definidos
- [ ] Politicas de consentimento, privacidade e visibilidade foram conectadas ao cadastro
- [ ] Regras de unicidade/merge de cadastro foram formalizadas

## Checklist de Code Review
- [ ] O mesmo responsavel nao e duplicado desnecessariamente por vinculo
- [ ] Dados sensiveis nao vazam para contextos sem necessidade
- [ ] Alteracoes cadastrais sensiveis deixam trilha de auditoria
- [ ] Regras de acesso respeitam tenant, papel e vinculo de responsabilidade

## Checklist de Testes
- [ ] Existem testes para estudante com multiplos responsaveis
- [ ] Existem testes para responsavel vinculado a multiplos estudantes
- [ ] Existem testes de restricao de visibilidade/acesso
- [ ] Existem testes de merge/unicidade de cadastro

## Checklist de Documentacao
- [ ] Casos de uso de estudante e responsavel foram oficializados
- [ ] Politicas de privacidade e classificacao de dados estao alinhadas
- [ ] API futura define claramente o que pode ser exposto nesses cadastros

