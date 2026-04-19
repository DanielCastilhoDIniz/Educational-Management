# Plano de Refatoracao do Fluxo de Criacao de Matricula

## Status

**Concluido** — TASKs 1 a 9 implementadas para o escopo atual do fluxo de criacao.

## Objetivo

Consolidar o desenho do fluxo de criacao de matricula para que o contrato de
persistencia, a taxonomia de erros e a implementacao do adapter Django contem a
mesma historia.

Este plano foca principalmente em:

- [enrollment_repository.py](/d:/TI/School_management/Education_manegment/src/application/academic/enrollment/ports/enrollment_repository.py)
- [create_enrollment.py](/d:/TI/School_management/Education_manegment/src/application/academic/enrollment/services/create_enrollment.py)
- [django_enrollment_repository.py](/d:/TI/School_management/Education_manegment/src/infrastructure/django/apps/academic/repositories/django_enrollment_repository.py)

## Decisoes Consolidadas

1. `create(...)` e exclusivo para persistir uma matricula nova.
2. O port fica enxuto com `get_by_id(...)`, `save(...)` e `create(...)`.
3. `exist_by_business_key(...)` foi removido do contrato e do fluxo principal.
4. A unicidade final e garantida na persistencia, nao por pre-check.
5. A Application cria o aggregate e tenta persistir diretamente.
6. `EnrollmentCreationError` foi removido do fluxo por gerar ambiguidade contratual.
7. O contrato minimo de falhas do `create(...)` fica:
   - `EnrollmentDuplicationError`
   - `EnrollmentTechnicalPersistenceError`
8. `EnrollmentDuplicationError` cobre:
   - duplicidade por business key
   - colisao explicita de `id`
9. `EnrollmentTechnicalPersistenceError` cobre:
   - falhas tecnicas de banco/servidor
   - violacoes de integridade inesperadas nao classificadas como duplicidade
10. O adapter Django importa `EnrollmentDuplicationError` e
    `EnrollmentTechnicalPersistenceError` da Application, porque ja implementa
    o port dessa camada.
11. O `create()` do adapter nao usa `except Exception` generico.
12. A classificacao de duplicidade e conservadora.
13. `EnrollmentDuplicationError` so e emitido quando houver evidencia tecnica
    suficiente.
14. Evidencia tecnica suficiente significa, no schema atual:
    - `pgcode == "23505"` (unique violation no PostgreSQL)
    - com `constraint_name` registrado em `details` quando estiver disponivel
15. Se o model passar a ter outras `unique constraints` com semantica diferente,
    a regra deve ser endurecida para tambem inspecionar `constraint_name`.
16. Se houver `IntegrityError` sem evidencia tecnica suficiente de duplicidade,
    o erro cai em `EnrollmentTechnicalPersistenceError`.
17. `DatabaseError` e `IntegrityError` nao duplicado sao distinguidos por
    `code/details` dentro de `EnrollmentTechnicalPersistenceError`.
18. O acoplamento especifico ao PostgreSQL fica confinado ao adapter Django.
19. A docstring do `create(...)` no port explicita:
    - que a unicidade final e garantida na persistencia
    - que duplicidade vem por `EnrollmentDuplicationError`
    - que as demais falhas vem por `EnrollmentTechnicalPersistenceError`
20. `EnrollmentTechnicalPersistenceError` tambem e usado no `save()` para falhas
    tecnicas de banco, substituindo `InfrastructureError` no contrato da
    application.

## Contrato Operacional de `create(...)`

- Persiste um aggregate novo e retorna a versao inicial persistida.
- E exclusivo para criacao de novas matriculas.
- Falha com `EnrollmentDuplicationError` quando houver colisao de `id` ou
  business key.
- A unicidade final e garantida na persistencia.
- Demais falhas tecnicas ou de integridade inesperada sao levantadas como
  `EnrollmentTechnicalPersistenceError`.

## Tasks

### TASK 1 - Consolidar o contrato do port EnrollmentRepository [CONCLUIDA]

**Escopo executado**

- removido `exist_by_business_key(...)`
- docstring de `create(...)` revisada
- `EnrollmentDuplicationError` e `EnrollmentTechnicalPersistenceError` explicitados
- unicidade final garantida na persistencia registrada
- duplicidade cobre business key e colisao de `id`

### TASK 2 - Remover EnrollmentCreationError do fluxo de criacao [CONCLUIDA]

**Escopo executado**

- `EnrollmentCreationError` removido de todos os lancamentos, catches e imports
- classe removida de `persistence_errors.py`
- fluxo de criacao trabalha apenas com `EnrollmentDuplicationError`
  e `EnrollmentTechnicalPersistenceError`

### TASK 3 - Remover pre-check do fluxo principal de create [CONCLUIDA]

**Escopo executado**

- `exist_by_business_key(...)` removido do service, port e adapter
- criacao nao depende mais de verificacao previa

### TASK 4 - Implementar classificacao conservadora de duplicidade no adapter Django [CONCLUIDA]

**Escopo executado**

- `IntegrityError` tratado explicitamente no adapter
- duplicidade confirmada por `pgcode == "23505"`
- ausencia de evidencia suficiente cai em `EnrollmentTechnicalPersistenceError`

### TASK 5 - Separar integridade inesperada de falha de banco [CONCLUIDA]

**Escopo executado**

- ramo proprio para `IntegrityError` nao duplicado com `code=ENROLLMENT_CREATION_FAILED`
- ramo proprio para `DatabaseError` com `code=DATABASE_ERROR`
- mensagens distintas para diagnostico

### TASK 6 - Remover catch genérico do create() [CONCLUIDA]

**Escopo executado**

- `except Exception` removido do `create()` do adapter
- `except Exception` removido do `finalize_state_change` no `_state_change_flow.py`
- apenas erros previstos pelo contrato sao traduzidos

### TASK 7 - Alinhar o service CreateEnrollment ao contrato novo [CONCLUIDA]

**Escopo executado**

- service captura `EnrollmentDuplicationError` e `EnrollmentTechnicalPersistenceError`
- catches obsoletos removidos
- logica de pre-check removida
- `finalize_state_change` alinhado ao mesmo contrato para o fluxo de `save()`

### TASK 8 - Atualizar testes do fluxo de criacao [CONCLUIDA]

**Escopo executado**

- fakes atualizados: `InMemoryEnrollmentRepository.create()` simula duplicidade
- `FailingEnrollmentRepository` levanta `EnrollmentTechnicalPersistenceError`
- `FailingCreateInRepository` removido (codigo morto)
- `exist_by_business_key(...)` removido dos fakes
- testes de service atualizados para `DATABASE_ERROR`
- teste de infra atualizado para `EnrollmentTechnicalPersistenceError`

**Observacao**

- a suite atual ja cobre sucesso, duplicidade por business key, colisao explicita de `id` e falha tecnica tipada no adapter
- como endurecimento futuro, ainda vale adicionar uma assercao explicita de ausencia de persistencia parcial no teste de falha tecnica

### TASK 9 - Atualizar documentacao oficial [CONCLUIDA]

**Escopo executado**

- ADR 012 atualizado com `EnrollmentTechnicalPersistenceError`
- checklists do ADR 012 atualizados
- `criar_matricula.md` atualizado: pre-check removido, taxonomia final de erros aplicada, estado atual da implementacao corrigido

### TASK 10 - Refatorar a tipagem contratual dos erros de persistencia [PLANEJADA]

**Objetivo**

- remover a dependencia de `cast(...)` nos services da matricula
- manter `ApplicationPersistenceError` generica
- introduzir uma fronteira contratual tipada apenas no contexto `academic.enrollment`
- tratar esta refatoracao como ajuste local de contexto, nao como primeiro passo de extracao para `application/shared/`

**Escopo previsto**

- manter `ApplicationPersistenceError` desacoplada de `ErrorCodes`
- criar uma subclasse intermediaria para erros de persistencia da matricula que ja podem ser expostos com `ErrorCodes`
- nao criar abstracoes em `application/shared/` nesta etapa
- migrar `EnrollmentDuplicationError` e `EnrollmentTechnicalPersistenceError` para essa intermediaria
- avaliar se `ConcurrencyConflictError` e `EnrollmentPersistenceNotFoundError` devem permanecer traduzidos pela Application
- remover `cast(...)` dos call sites em `create_enrollment.py` e `_state_change_flow.py` onde o erro ja for contratual
- adicionar cobertura de teste na Application para preservacao do `code` tecnico vindo do repositorio
- alinhar a documentacao da taxonomia final

**Documento de apoio**

- ver [plano_refatoracao_tipagem_erros_persistencia_enrollment.md](/d:/TI/School_management/Education_manegment/docs/backlog/plano_refatoracao_tipagem_erros_persistencia_enrollment.md)

## Ordem Recomendada

1. ~~TASK 1~~ concluida
2. ~~TASK 2~~ concluida
3. ~~TASK 3~~ concluida
4. ~~TASK 4~~ concluida
5. ~~TASK 5~~ concluida
6. ~~TASK 6~~ concluida
7. ~~TASK 7~~ concluida
8. ~~TASK 8~~ concluida
9. ~~TASK 9~~ concluida
10. TASK 10 - planejada: tipagem contratual dos erros de persistencia
