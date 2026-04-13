# Visao de Produto - SaaS de Gestao Escolar

## Objetivo
Descrever o escopo funcional maior do produto para orientar arquitetura, contextos, contratos e backlog documental.

## Capacidades de Negocio Esperadas
- cadastro e governanca de instituicoes
- cadastro de usuarios e vinculo a instituicoes
- controle de papeis como administrador, secretaria, professor e responsavel
- cadastro de estudantes e seus contatos
- cadastro de responsaveis e vinculo com estudantes
- cadastro de professores e suas atribuicoes
- organizacao academica por ano letivo, periodos, turmas e disciplinas
- matricula de estudantes em turmas e periodos
- registro de aulas ministradas
- lancamento de frequencia
- configuracao de avaliacoes por instituicao e periodo
- lancamento de notas e calculo de medias
- fechamento de periodo e emissao de resultados
- consultas administrativas, pedagogicas e operacionais

## Caracteristicas de SaaS
- multi-tenancy por instituicao
- configuracao institucional por escopo
- isolamento de dados entre tenants
- observabilidade e auditoria por tenant
- trilha de autorizacao por papel e escopo
- base para cobranca, planos e modulos futuros

## Contextos Principais Sugeridos
- identidade e acesso
- organizacao institucional
- cadastro academico
- matriculas
- diario de classe
- avaliacao e boletim
- contatos e responsaveis
- auditoria e observabilidade

## Principais Riscos Arquiteturais
- misturar politicas institucionais no dominio central
- acoplar matricula a tudo cedo demais
- nao definir fronteira clara entre turma, disciplina, diario e avaliacao
- crescer sem modelo forte de autorizacao e isolamento multi-tenant
- adiar demais contratos de fechamento de periodo e registros oficiais

## Objetivo Documental
Este documento orienta os demais ADRs, casos de uso e politicas do pacote proposto.
