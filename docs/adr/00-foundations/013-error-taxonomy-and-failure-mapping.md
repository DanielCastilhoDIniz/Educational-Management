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

#### Autorizacao
- `AUTHZ_USER_LOCKED` — conta suspensa ou inativa globalmente
- `AUTHZ_INSUFFICIENT_PRIVILEGES` — papel nao possui o escopo necessario para a acao
- `AUTHZ_TENANT_MISMATCH` — tentativa de acesso a dados de outro tenant
- `AUTHZ_OUTSIDE_WINDOW` — acao bloqueada por restricao temporal (ex: lancamento fora da janela letiva)
- `AUTHORIZATION_DENIED` — fallback generico para negacoes nao classificadas

#### Negocio e Dominio
- `DUPLICATE_ENROLLMENT` — matricula duplicada
- `DUPLICATE_MEMBERSHIP` — vinculo institucional duplicado
- `DUPLICATE_USER` — documento legal ja cadastrado no sistema
- `MEMBERSHIP_INACTIVE_CONFLICT` — vinculo inativo encontrado, requer caso de uso de reativacao
- `POLICY_VIOLATION` — violacao de politica de negocio
- `INVALID_STATE_TRANSITION` — transicao de estado invalida
- `JUSTIFICATION_REQUIRED` — justificativa obrigatoria nao fornecida
- `CONCURRENCY_CONFLICT` — conflito de escrita concorrente no mesmo aggregate

#### Busca e Recuperacao
- `ENROLLMENT_NOT_FOUND` — matricula nao encontrada
- `ENROLLMENT_NOT_ACTIVE` — matricula nao esta ativa
- `CONCLUSION_NOT_ALLOWED` — conclusao nao permitida para o estado atual

#### Tecnico
- `DATA_INTEGRITY_ERROR` — violacao de constraint de banco
- `UNEXPECTED_ERROR` — erro nao classificado

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

## Checklist de Implementacao
- [x] Existem erros de dominio, application e persistencia separados no modulo
- [x] `ErrorCodes` base ja foram definidos na Application
- [x] Existe mapper de erro de domínio para erro de application
- [ ] Falhas de persistencia sao mapeadas de ponta a ponta para codigos estaveis
- [ ] Payload HTTP padronizado consome a mesma taxonomia de erros

## Checklist de Code Review
- [x] O dominio nao vaza excecao como contrato para camadas superiores
- [ ] A infraestrutura nao colapsa todas as falhas em erro generico
- [ ] A interface usa `code` estavel em vez de depender do nome da excecao
- [ ] Detalhes sensiveis nao vazam para payloads externos

## Checklist de Testes
- [x] Existem testes de mapeamento de erros de dominio para application
- [ ] Existem testes para mapeamento de falhas de persistencia
- [ ] Existe teste garantindo `UNEXPECTED_ERROR` para falha nao classificada
- [ ] Existe teste de mapeamento `ErrorCodes -> HTTP` quando a API existir

## Checklist de Documentacao
- [ ] Catalogo oficial de erros esta documentado e atualizado
- [ ] Casos de uso listam falhas esperadas usando os mesmos codigos
- [ ] Documentacao de observabilidade referencia a mesma taxonomia

