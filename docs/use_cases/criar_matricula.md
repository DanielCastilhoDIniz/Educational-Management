# Caso de Uso - Criar Matricula

## Objetivo
Registrar uma nova matricula valida para um estudante em uma instituicao, turma e periodo academico especificos.

## Atores
- secretaria
- sistema
- integracao autorizada

## Entrada Conceitual
- `institution_id`
- `student_id`
- `class_group_id`
- `academic_period_id`
- `actor_id`
- `occurred_at` opcional
- metadados institucionais necessarios para politicas externas

## Regras de Entrada Ja Definidas
- `institution_id` e obrigatorio na criacao
- toda matricula pertence a uma instituicao explicita
- estudante, turma e periodo academico devem ser coerentes com o mesmo escopo institucional esperado
- a criacao e separada do fluxo de `save()` de update

## Pre-condicoes
- instituicao existe e esta apta no contexto informado
- estudante existe e esta apto ao vinculo
- turma existe e aceita matriculas
- periodo academico permite criacao
- nao existe matricula duplicada segundo a politica vigente
- ator esta autorizado

## Fluxo Principal
1. Receber os dados de criacao da matricula.
2. Resolver o contexto institucional da operacao.
3. Validar autorizacao do ator.
4. Resolver politicas de criacao e unicidade.
5. Verificar existencia de matricula conflitante.
6. Instanciar o aggregate novo em estado `active`.
7. Registrar o evento de dominio `EnrollmentCreated`.
8. Persistir o snapshot inicial com versao `1`.
9. Retornar resultado estavel para a camada superior.

## Estado Atual da Implementacao
- o aggregate `Enrollment.create(...)` ja existe
- o service `CreateEnrollment.execute(...)` ja existe
- `institution_id` ja e exigido pelo service e pelo dominio
- o evento `EnrollmentCreated` ja foi adotado e ja e emitido na criacao
- as validacoes de autorizacao, politicas externas e duplicidade ainda dependem dos contextos de usuarios, membership, politicas e cadastro mestre
- por isso, essas validacoes permanecem pendentes na implementacao atual e devem ser tratadas como dependencias explicitas da evolucao do caso de uso
- a persistencia inicial completa ainda depende da implementacao concreta de `repo.create(...)` no adapter principal de infraestrutura

## Fluxos Alternativos
- duplicidade de negocio: falha esperada
- janela de matricula encerrada: falha esperada
- ator nao autorizado: falha esperada
- erro tecnico de integridade: falha esperada tipada

## Pos-condicoes
- matricula existe em persistencia quando o adapter concreto de criacao estiver implementado
- `state = active`
- `version = 1`
- `reactivated_at = null`
- `EnrollmentCreated` foi registrado no buffer de eventos do aggregate

## Politicas Consultadas
- politica de criacao de matricula
- politica de autorizacao e matriz de atores
- politica de timestamps e UTC

## Observacoes
- `institution_id` nao e apenas um dado de transporte; ele faz parte do contrato de criacao da matricula
- a existencia do fluxo funcional nao significa que todas as dependencias de autorizacao e politica ja estejam implementadas
- a emissao de `EnrollmentCreated` ja nao esta mais em aberto: ela foi decidida e implementada no dominio
- este documento descreve o contrato alvo do caso de uso e sinaliza explicitamente o que ja existe e o que ainda esta pendente
