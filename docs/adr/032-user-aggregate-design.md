# ADR 032 - Design do Aggregate User

## Status
Proposto

## Contexto
O sistema precisa representar a identidade global de uma pessoa — independente de qualquer instituicao. O ADR 020 estabeleceu a separacao conceitual entre identidade global (`User`) e vinculo institucional (`Membership`). Este ADR define as decisoes de design do aggregate `User`.

## Decisao
Modelar `User` como aggregate root responsavel pela identidade global da pessoa no sistema.

## Campos do Aggregate

| Campo            | Tipo     | Obrigatorio | Imutavel | Descricao                                                  |
|------------------|----------|-------------|----------|------------------------------------------------------------|
| `id`             | UUID     | sim         | sim      | identidade tecnica do usuario                              |
| `legal_identity` | VO       | sim         | nao      | documento legal de identificacao (CPF, certidao, passaporte) |
| `full_name`      | string   | sim         | nao      | nome completo da pessoa                                    |
| `email`          | string   | nao         | nao      | email de contato, opcional para menores                    |
| `birth_date`     | date     | sim         | sim      | data de nascimento                                         |
| `guardian_id`    | UUID     | nao         | nao      | referencia ao `User` responsavel legal, obrigatorio para menores de 18 anos |
| `state`          | enum     | sim         | nao      | estado atual da conta                                      |
| `created_by`     | string   | sim         | sim      | audit trail da criacao                                     |
| `created_at`     | datetime | sim         | sim      | timestamp de criacao (UTC)                                 |

## Value Object LegalIdentity

| Campo               | Tipo   | Obrigatorio | Descricao                                               |
|---------------------|--------|-------------|---------------------------------------------------------|
| `identity_type`     | enum   | sim         | tipo do documento: CPF, CERTIDAO_NASCIMENTO, PASSPORT   |
| `identity_number`   | string | sim         | numero do documento                                     |
| `identity_issuer`   | string | nao         | orgao emissor, obrigatorio para certidao e passaporte   |

Regras do `LegalIdentity`:
- `identity_issuer` e obrigatorio quando `identity_type` for `CERTIDAO_NASCIMENTO` ou `PASSPORT`
- `identity_issuer` e dispensavel quando `identity_type` for `CPF`
- `identity_number` deve ser unico por `identity_type` no sistema

## Chave de Negocio
Unicidade garantida por `(identity_type, identity_number)`.

## Relacao com Django auth
O aggregate `User` representa a identidade de negocio. O mecanismo de autenticacao (senha, OAuth, tokens) e responsabilidade do `auth.User` do Django.

A referencia cruzada e mantida no `UserModel` de infraestrutura, que carrega tanto o `id` do dominio quanto a FK para o `auth.User`. O dominio nao conhece detalhes do framework de autenticacao.

## guardian_id
- Referencia o `id` de outro `User` (responsavel legal)
- Obrigatorio para usuarios menores de 18 anos — validado pela Application com base em `birth_date`
- O dominio carrega apenas o UUID, sem acessar o aggregate do guardiao diretamente

## Matriz de Estados

### `PENDING` (estado inicial)
Campos obrigatorios:
- `created_at`

Interpretacao:
- usuario criado mas ainda nao confirmado ou verificado
- pode representar pre-cadastro para reserva de vaga
- nao pode ter `Membership` criado enquanto estiver neste estado

### `ACTIVE`
Campos obrigatorios:
- `created_at`

Interpretacao:
- usuario verificado e operacional
- pode ter `Membership` criado

### `SUSPENDED`
Campos obrigatorios:
- `created_at`

Interpretacao:
- bloqueio temporario da conta (ex: conta comprometida, pendencia administrativa)
- os `Membership` associados nao mudam de estado, mas o acesso e negado pela camada de autorizacao que verifica `User.state` antes de permitir qualquer operacao via `Membership`

### `INACTIVE`
Campos obrigatorios:
- `created_at`

Interpretacao:
- encerramento definitivo da conta
- estado terminal, sem transicoes de saida

## Transicoes Permitidas
- `PENDING -> ACTIVE` (confirmacao ou verificacao da identidade)
- `PENDING -> INACTIVE` (cancelamento antes de ativar)
- `ACTIVE -> SUSPENDED` (bloqueio temporario)
- `ACTIVE -> INACTIVE` (encerramento definitivo)
- `SUSPENDED -> ACTIVE` (desbloqueio)
- `SUSPENDED -> INACTIVE` (encerramento durante suspensao)

## Transicoes Proibidas
- qualquer transicao para `PENDING` — e estado exclusivamente inicial
- qualquer transicao a partir de `INACTIVE` — e estado terminal
- `ACTIVE -> ACTIVE`, `SUSPENDED -> SUSPENDED` como operacao de negocio

## Registro de Transicoes
Cada transicao de estado e registrada por um `UserTransition` (Value Object), aplicando o mesmo padrao do `StateTransition` do aggregate `Enrollment`.

Campos obrigatorios do `UserTransition`:
- `from_state` — estado anterior
- `to_state` — estado resultante
- `occurred_at` — timestamp da transicao (UTC)
- `actor_id` — quem executou a transicao
- `reason` — justificativa, quando aplicavel

## Responsabilidades da Application
- Validar unicidade de `(identity_type, identity_number)` antes de criar o `User`
- Validar que `guardian_id` esta presente para usuarios menores de 18 anos
- Validar que o `User` esta em estado `ACTIVE` antes de criar um `Membership`
- Conectar o `User` de dominio ao `auth.User` do Django via `UserModel`

## Plano de Implementacao
- Definir `UserState` enum com `PENDING`, `ACTIVE`, `SUSPENDED`, `INACTIVE`
- Definir `LegalIdentityType` enum com `CPF`, `CERTIDAO_NASCIMENTO`, `PASSPORT`
- Implementar VO `LegalIdentity` com validacao de `identity_issuer`
- Implementar aggregate `User` com factory method `create()`
- Implementar `UserTransition` Value Object
- Implementar caso de uso `CadastrarUsuario`
- Implementar caso de uso `AtivarUsuario`
- Atualizar pre-condicao de `VincularUsuarioAInstituicaoEPapel`: exigir `User` em `ACTIVE`

## Checklist de Implementacao
- [ ] Aggregate `User` com todos os campos definidos neste ADR
- [ ] VO `LegalIdentity` com validacao de tipo e emissor
- [ ] `UserState` enum com quatro estados
- [ ] `UserTransition` Value Object implementado
- [ ] Factory method `User.create()` nasce em `PENDING`
- [ ] Validacao de `guardian_id` obrigatorio para menores delegada para a Application
- [ ] Chave de negocio `(identity_type, identity_number)` com constraint no banco
- [ ] `UserModel` carrega FK para `auth.User` do Django

## Checklist de Code Review
- [ ] O dominio nao referencia `auth.User` nem detalhes do Django
- [ ] `birth_date` e imutavel apos criacao
- [ ] `guardian_id` nao e acessado como objeto — apenas como UUID
- [ ] Transicoes proibidas lancam erros de dominio, nao excecoes genericas

## Checklist de Testes
- [ ] Existem testes de criacao de `User` em estado `PENDING`
- [ ] Existem testes de transicao para cada aresta permitida
- [ ] Existem testes de invariante para cada transicao proibida
- [ ] Existem testes de `LegalIdentity` para cada tipo de documento
- [ ] Existe teste de negacao: `Membership` nao pode ser criado para `User` em `PENDING`

## Checklist de Documentacao
- [ ] Use cases `CadastrarUsuario` e `AtivarUsuario` documentados
- [ ] Pre-condicao de `VincularUsuarioAInstituicaoEPapel` atualizada para exigir `User ACTIVE`
- [ ] ADR 020 atualizado para referenciar este ADR como detalhamento do aggregate `User`
