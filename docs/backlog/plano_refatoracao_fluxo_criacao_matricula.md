# Plano de Refatoracao do Fluxo de Criacao de Matricula

## Status

**Concluido** — TASKs 1 a 7 e 9 implementadas. TASK 8 parcialmente pendente (testes de integracao do adapter).

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
14. Evidencia tecnica suficiente significa:
    - `pgcode == "23505"` (unique violation no PostgreSQL)
    - `constraint_name == "unique_enrollment"`
    - combinacao dos dois, nao apenas suspeita
15. Se houver `IntegrityError` sem evidencia tecnica suficiente de duplicidade,
    o erro cai em `EnrollmentTechnicalPersistenceError`.
16. `DatabaseError` e `IntegrityError` nao duplicado sao distinguidos por
    `code/details` dentro de `EnrollmentTechnicalPersistenceError`.
17. O acoplamento especifico ao PostgreSQL fica confinado ao adapter Django.
18. A docstring do `create(...)` no port explicita:
    - que a unicidade final e garantida na persistencia
    - que duplicidade vem por `EnrollmentDuplicationError`
    - que as demais falhas vem por `EnrollmentTechnicalPersistenceError`
19. `EnrollmentTechnicalPersistenceError` tambem e usado no `save()` para falhas
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
- duplicidade confirmada por `pgcode == "23505"` e `constraint_name == "unique_enrollment"`
- ausencia de evidencia suficiente cai em `EnrollmentTechnicalPersistenceError`

### TASK 5 - Separar integridade inesperada de falha de banco [CONCLUIDA]

**Escopo executado**

- ramo proprio para `IntegrityError` nao duplicado com `code=ENROLLMENT_CREATION_FAILED`
- ramo proprio para `DatabaseError` com `code=ENROLLMENT_CREATION_FAILED`
- mensagens distintas para diagnostico

### TASK 6 - Remover catch generico do create() [CONCLUIDA]

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

### TASK 8 - Atualizar testes do fluxo de criacao [PARCIALMENTE CONCLUIDA]

**Escopo executado**

- fakes atualizados: `InMemoryEnrollmentRepository.create()` simula duplicidade
- `FailingEnrollmentRepository` levanta `EnrollmentTechnicalPersistenceError`
- `FailingCreateInRepository` removido (codigo morto)
- `exist_by_business_key(...)` removido dos fakes
- testes de service atualizados para `DATABASE_ERROR`
- teste de infra atualizado para `EnrollmentTechnicalPersistenceError`

**Pendente**

- testes de integracao do adapter para criacao bem-sucedida
- testes de duplicidade tipada no adapter com banco real
- testes de falha tecnica no adapter com banco real

### TASK 9 - Atualizar documentacao oficial [CONCLUIDA]

**Escopo executado**

- ADR 012 atualizado com `EnrollmentTechnicalPersistenceError`
- checklists do ADR 012 atualizados
- `criar_matricula.md` atualizado: pre-check removido, taxonomia final de erros aplicada, estado atual da implementacao corrigido

## Ordem Recomendada

1. ~~TASK 1~~ concluida
2. ~~TASK 2~~ concluida
3. ~~TASK 3~~ concluida
4. ~~TASK 4~~ concluida
5. ~~TASK 5~~ concluida
6. ~~TASK 6~~ concluida
7. ~~TASK 7~~ concluida
8. TASK 8 — pendente: testes de integracao do adapter
9. ~~TASK 9~~ concluida
