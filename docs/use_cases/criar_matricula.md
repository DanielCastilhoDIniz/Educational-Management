# Caso de Uso - Criar Matricula

## Objetivo
Registrar uma nova matricula valida para um estudante em uma turma e periodo academico especificos.

## Atores
- secretaria
- sistema
- integracao autorizada

## Entrada Conceitual
- `student_id`
- `class_group_id`
- `academic_period_id`
- `actor_id`
- `occurred_at` opcional
- metadados institucionais necessarios para politicas externas

## Pre-condicoes
- estudante existe e esta apto ao vinculo
- turma existe e aceita matriculas
- periodo academico permite criacao
- nao existe matricula duplicada segundo a politica vigente
- ator esta autorizado

## Fluxo Principal
1. Validar autorizacao do ator.
2. Resolver politicas de criacao e unicidade.
3. Verificar existencia de matricula conflitante.
4. Instanciar o aggregate novo em estado `active`.
5. Persistir o snapshot inicial com versao `1`.
6. Registrar auditoria e, se adotado, emitir `EnrollmentCreated`.
7. Retornar resultado estavel para a camada superior.

## Fluxos Alternativos
- duplicidade de negocio: falha esperada
- janela de matricula encerrada: falha esperada
- ator nao autorizado: falha esperada
- erro tecnico de integridade: falha esperada tipada

## Pos-condicoes
- matricula existe em persistencia
- `state = active`
- `version = 1`
- `reactivated_at = null`

## Politicas Consultadas
- politica de criacao de matricula
- politica de autorizacao e matriz de atores
- politica de timestamps e UTC
