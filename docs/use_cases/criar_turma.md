# Caso de Uso - Criar Turma

## Objetivo
Registrar uma turma em determinado ano letivo e periodo, pronta para receber estudantes, disciplinas e professores.

## Atores
- secretaria
- administrador institucional

## Entrada Conceitual
- `institution_id`
- `school_year_id`
- `period_id`
- identificador/nome da turma
- metadados pedagogicos relevantes

## Pre-condicoes
- ano e periodo existem
- ator autorizado
- chave de negocio da turma e unica no escopo definido

## Fluxo Principal
1. Validar autorizacao.
2. Validar consistencia com ano e periodo.
3. Criar turma.
4. Registrar auditoria.
5. Retornar identificador da turma.
