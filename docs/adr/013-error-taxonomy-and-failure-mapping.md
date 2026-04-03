# ADR 013 - Taxonomia de Erros e Mapeamento entre Camadas

## Status
Proposto

## Contexto
O modulo ja diferencia erros de dominio, aplicacao e persistencia, mas ainda ha lacunas no mapeamento de ponta a ponta. Isso dificulta contratos estaveis para API, observabilidade e suporte operacional.

## Decisao
Adotar uma taxonomia de erros explicita, com responsabilidades por camada.

## Categorias

### Dominio
Erros de regra e invariantes do aggregate.

Exemplos:
- transicao invalida
- justificativa obrigatoria
- conclusao nao permitida
- matricula nao ativa

### Application
Erros estaveis expostos para camadas superiores.

Codigos minimos sugeridos:
- `ENROLLMENT_NOT_FOUND`
- `INVALID_STATE_TRANSITION`
- `JUSTIFICATION_REQUIRED`
- `ENROLLMENT_NOT_ACTIVE`
- `CONCLUSION_NOT_ALLOWED`
- `CONCURRENCY_CONFLICT`
- `DATA_INTEGRITY_ERROR`
- `AUTHORIZATION_DENIED`
- `POLICY_VIOLATION`
- `UNEXPECTED_ERROR`

### Persistencia / Infra
Erros tecnicos tipados para o adaptador.

Exemplos:
- `EnrollmentPersistenceNotFoundError`
- `ConcurrencyConflictError`
- `DataIntegrityPersistenceError`
- `InfrastructureError`

### Interface
Mapeamento final para HTTP, fila, CLI ou jobs.

Exemplos de HTTP:
- not found -> 404
- dominio/validacao -> 400 ou 409 conforme o caso
- concorrencia -> 409
- autorizacao -> 403
- erro tecnico inesperado -> 500

## Consequencias

### Positivas
- contrato externo mais previsivel
- logs e dashboards ficam mais legiveis
- menos acoplamento a mensagens textuais de excecao

### Negativas / Riscos
- exige disciplina para nao jogar tudo em `UNEXPECTED_ERROR`
- aumenta a quantidade de tipos e testes de traducao

## Regras e Invariantes
- regra de dominio nao deve virar erro tecnico generico
- erro tecnico nao deve vazar como mensagem de banco para fora do sistema
- `UNEXPECTED_ERROR` deve ser excecao, nao categoria padrao para tudo
- a Application deve traduzir erros de persistencia conhecidos para `ErrorCodes` estaveis

## Plano de Implementacao
- listar erros tecnicos ja existentes
- criar mapeamento Application -> ErrorCodes faltantes
- revisar testes de traducao de erros
- documentar mapeamento final para interface HTTP
