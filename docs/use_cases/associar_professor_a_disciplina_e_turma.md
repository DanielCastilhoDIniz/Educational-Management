# Caso de Uso - Associar Professor a Disciplina e Turma

## Objetivo
Vincular um professor a uma disciplina ofertada para uma turma em um periodo especifico.

## Atores
- secretaria
- coordenacao
- administrador institucional

## Entrada Conceitual
- `teacher_id`
- `subject_id`
- `class_group_id`
- `period_id`
- vigencia e carga atribuida, quando aplicavel

## Pre-condicoes
- professor existe
- disciplina existe
- turma existe
- ator autorizado
- vinculo permitido pela politica institucional

## Fluxo Principal
1. Validar autorizacao.
2. Validar consistencia academica da oferta.
3. Criar atribuicao.
4. Registrar auditoria.
5. Retornar contrato estavel.
