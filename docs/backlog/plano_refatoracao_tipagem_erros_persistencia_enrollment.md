# Plano de Refatoracao da Tipagem dos Erros de Persistencia de Enrollment

## Objetivo

Eliminar a necessidade de `cast(...)` nos services da matricula sem acoplar a
classe base compartilhada aos enums de erro do contexto `academic.enrollment`.

O alvo e melhorar o contrato estatico da taxonomia de erros, mantendo a base
generica e deslocando o acoplamento tipado apenas para o contexto que realmente
precisa dele.

## Problema Atual

Hoje o projeto convive com tres fatos ao mesmo tempo:

- `ApplicationPersistenceError` e generica e usa `code` como `str`
- os services da matricula esperam trabalhar com `ErrorCodes` estaveis
- por causa disso, os call sites precisam usar `cast(...)` para reaproveitar
  `e.code`

Isso nao quebra o comportamento atual, mas enfraquece o contrato tipado da
Application e espalha a responsabilidade de confiar no `code` para fora da
hierarquia de erros.

## Decisao Arquitetural Recomendada

Manter `ApplicationPersistenceError` generica e introduzir uma subclasse
intermediaria especifica para erros de persistencia da matricula que ja sao
seguros para expor com `ErrorCodes`.

### Hierarquia alvo

- `ApplicationPersistenceError`
  Continua sendo a base comum e generica.
  Nao conhece `ErrorCodes`.

- `EnrollmentExposablePersistenceError`
  Nova subclasse intermediaria do contexto `academic.enrollment`.
  Responsabilidade:
  - representar erros de persistencia da matricula que ja atravessam a
    Application com `code` estavel
  - tipar o `code` como `ErrorCodes`

- `EnrollmentDuplicationError`
  Passa a herdar de `EnrollmentExposablePersistenceError`

- `EnrollmentTechnicalPersistenceError`
  Passa a herdar de `EnrollmentExposablePersistenceError`

### Erros que permanecem fora da intermediaria

- `ConcurrencyConflictError`
- `EnrollmentPersistenceNotFoundError`

Motivo:

- hoje esses dois casos ainda sao reinterpretados pela Application
- eles nao estao sendo simplesmente reaproveitados com o `code` original
- manter esses tipos fora da intermediaria evita misturar erros reaproveitados
  com erros traduzidos deliberadamente

## O Que Deve Ser Construido

### 1. Reorganizar a hierarquia de erros

Em `src/application/academic/enrollment/errors/persistence_errors.py`:

- preservar `ApplicationPersistenceError` como base generica
- criar `EnrollmentExposablePersistenceError`
- mover `EnrollmentDuplicationError` e `EnrollmentTechnicalPersistenceError`
  para herdar dela
- atualizar docstrings para explicar a diferenca entre:
  - base generica
  - erro contratual exposto
  - erro ainda traduzido pela Application

### 2. Limpar os call sites do fluxo de criacao

Em `src/application/academic/enrollment/services/create_enrollment.py`:

- remover o `cast(...)` no ramo de `EnrollmentTechnicalPersistenceError`
- reaproveitar diretamente o `code` da excecao
- manter o ramo de duplicidade explicito ou reaproveitar `e.code`

Recomendacao:

- manter duplicidade explicita se a leitura ficar mais clara
- reaproveitar `e.code` no erro tecnico, que e o ramo onde o problema atual
  realmente aparece

### 3. Limpar os call sites do fluxo de save

Em `src/application/academic/enrollment/services/_state_change_flow.py`:

- remover o `cast(...)` no ramo de `EnrollmentTechnicalPersistenceError`
- manter `ConcurrencyConflictError` com traducao explicita
- manter `EnrollmentPersistenceNotFoundError` com traducao explicita

Esse passo preserva a regra principal:

- erro contratual reaproveitavel atravessa com o proprio `code`
- erro que a Application ainda reinterpretar continua com `code` explicitado no
  service

### 4. Revisar os adapters

Em `src/infrastructure/django/apps/academic/repositories/django_enrollment_repository.py`:

- confirmar que `EnrollmentTechnicalPersistenceError` e
  `EnrollmentDuplicationError` continuam sendo levantados apenas com
  `ErrorCodes` do contexto
- confirmar que nao ha ramos escapando com codigos livres fora da taxonomia
  esperada

### 5. Revisar os fakes e testes da Application

Em `tests/application/fakes.py`:

- permitir que o fake de falha tecnica em `create()` seja parametrizado por
  `code`
- nao deixar o fake preso a um unico cenario tecnico

Em `tests/application/test_create_enrollment_service.py`:

- adicionar cenario em que o repositorio levanta
  `EnrollmentTechnicalPersistenceError` com `DATABASE_ERROR`
- verificar que o service preserva `DATABASE_ERROR`
- adicionar cenario em que o repositorio levanta
  `EnrollmentTechnicalPersistenceError` com `ENROLLMENT_CREATION_FAILED`
- verificar que o service preserva esse segundo `code`

Em `tests` que usam `_state_change_flow.py`:

- confirmar que `EnrollmentTechnicalPersistenceError` continua preservando o
  `code`
- confirmar que `ConcurrencyConflictError` e
  `EnrollmentPersistenceNotFoundError` continuam traduzidos explicitamente

### 6. Atualizar a documentacao

Atualizar, ao final:

- `docs/backlog/plano_refatoracao_fluxo_criacao_matricula.md`
- `docs/adr/012-create-enrollment-contract.md`

O que precisa ficar claro:

- quais erros atravessam com o proprio `code`
- quais erros ainda sao reinterpretados pela Application
- por que a base continua generica
- por que o acoplamento tipado fica localizado no contexto `Enrollment`

## Ordem Recomendada de Execucao

1. Ajustar a hierarquia de erros no modulo de persistencia da Application
2. Limpar `create_enrollment.py`
3. Limpar `_state_change_flow.py`
4. Revisar os adapters para coerencia da taxonomia
5. Atualizar fakes e testes da Application
6. Atualizar documentacao

## Como Validar

### Validacao de tipagem

Considerar a refatoracao bem-sucedida quando:

- `create_enrollment.py` nao precisar mais de `cast(...)`
- `_state_change_flow.py` nao precisar mais de `cast(...)` no ramo tecnico
- a base continuar desacoplada de `ErrorCodes`

### Validacao funcional

Considerar a refatoracao bem-sucedida quando:

- duplicidade continuar saindo como `DUPLICATE_ENROLLMENT`
- falha tecnica de banco continuar saindo como `DATABASE_ERROR`
- falha tecnica de integridade inesperada continuar saindo como
  `ENROLLMENT_CREATION_FAILED`
- a Application nao achatar esses `codes` novamente

### Validacao documental

Considerar a refatoracao bem-sucedida quando:

- a hierarquia nova estiver explicada sem ambiguidade
- a documentacao diferenciar erro reaproveitado de erro traduzido
- backlog, ADR e testes contarem a mesma historia

## Critério de Pronto

Esta refatoracao pode ser considerada pronta quando todos os pontos abaixo
forem verdadeiros:

- `ApplicationPersistenceError` continua generica
- existe uma subclasse intermediaria contratual especifica de `Enrollment`
- `EnrollmentDuplicationError` e `EnrollmentTechnicalPersistenceError` herdam
  dessa intermediaria
- os `cast(...)` saem dos services da matricula nos ramos onde o erro ja e
  contratual
- os testes da Application provam preservacao do `code` tecnico
- a documentacao final explica corretamente a nova fronteira de acoplamento

## Riscos e Cuidados

- nao relaxar os builders para aceitar `str` livremente, senao a Application
  pode voltar a vazar codigos internos sem perceber
- nao incluir cedo demais `ConcurrencyConflictError` e
  `EnrollmentPersistenceNotFoundError` na intermediaria, porque isso misturaria
  erros reaproveitados com erros ainda traduzidos
- nao puxar `Generic` para toda a base agora, porque isso aumentaria a
  complexidade antes de existir repeticao suficiente em outros contextos
- nao mudar a taxonomia do adapter sem verificar antes se os testes e a
  documentacao ainda contam a mesma historia
