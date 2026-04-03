# Dados Mestres e Relacionamentos Principais

## Objetivo
Fornecer uma visao conceitual dos dados centrais que provavelmente sustentarao o SaaS.

## Entidades Conceituais Principais
- instituicao
- usuario
- membership institucional
- estudante
- responsavel
- professor
- disciplina
- ano letivo
- periodo letivo
- turma
- oferta de disciplina
- atribuicao de professor
- matricula
- aula registrada
- frequencia
- avaliacao
- nota
- consolidado de periodo

## Relacionamentos Principais
- uma instituicao possui usuarios, estudantes, professores, disciplinas, anos letivos e turmas
- um usuario pode ter memberships em mais de uma instituicao
- um estudante pode ter um ou mais responsaveis
- uma turma pertence a um periodo/ano letivo
- uma turma pode ofertar uma ou mais disciplinas, conforme modelo institucional
- professores podem ser associados a disciplinas e turmas
- matricula vincula estudante a turma/periodo
- frequencia e nota se referem a matriculas ou estudantes dentro da oferta academica
- consolidado de periodo depende de frequencia, notas e politicas da instituicao

## Recomendacao
Documentar explicitamente:
- chaves naturais e de negocio
- regras de unicidade por tenant
- regras de soft delete ou desativacao
- eventos importantes de cada entidade mestre
