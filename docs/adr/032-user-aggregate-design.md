# ADR 032 - Design do Aggregate User

## Status
Implementado.

## Contexto
O sistema precisa representar a identidade global de uma pessoa — independente de qualquer instituição. O ADR 020 estabeleceu a separação conceitual entre identidade global (`User`) e vinculo institucional (`Membership`). Este ADR define as decisões de design do aggregate `User`.

## Decisão
Modelar `User` como aggregate root responsável pela identidade global da pessoa no sistema.

## Campos do Aggregate

| Campo            | Tipo     | Obrigatório | Imutável | Descrição                                                  |
|------------------|----------|-------------|----------|------------------------------------------------------------|
| `id`             | UUID     | sim         | sim      | identidade técnica do usuário                              |
| `legal_identity` | VO       | sim         | nao      | documento legal de identificacao (CPF, certidão, passaporte) |
| `full_name`      | string   | sim         | nao      | nome completo da pessoa                                    |
| `email`          | string   | nao         | nao      | email de contato, opcional para menores                    |
| `birth_date`     | date     | sim         | sim      | data de nascimento                                         |
| `guardian_id`    | UUID     | nao         | nao      | referencia ao `User` responsável legal, obrigatório para menores de 18 anos |
| `state`          | enum     | sim         | nao      | estado atual da conta                                      |
| `created_by`     | string   | sim         | sim      | audit trail da criacao                                     |
| `created_at`     | datetime | sim         | sim      | timestamp de criacao (UTC)                                 |

## Value Object LegalIdentity

| Campo               | Tipo   | Obrigatorio | Descricao                                                            |
|---------------------|--------|-------------|----------------------------------------------------------------------|
| `identity_type`     | enum   | sim         | tipo do documento: CPF, CERTIDAO_NASCIMENTO, PASSPORT, CNH, RG, CNI.  |
| `identity_number`   | string | sim         | numero do documento                                                  |
| `identity_issuer`   | string | sim         | órgão emissor em todos documentos                                    |

Regras do `LegalIdentity`:
- `identity_number` deve ser único por `identity_type` no sistema



## Chave de Negocio
Unicidade garantida por `(identity_type, identity_number, identity_issuer)`.

## Relação com Django auth
O aggregate `User` representa a identidade de negocio. O mecanismo de autenticacao (senha, OAuth, tokens) e responsabilidade do `auth.User` do Django.

A referencia cruzada e mantida no `UserModel` de infraestrutura, que carrega tanto o `id` do domínio quanto a FK para o `auth.User`. O domínio nao conhece detalhes do framework de autenticacao.

## guardian_id
- Referencia o `id` de outro `User` (responsável legal)
- Obrigatório para usuários menores de 18 anos — validado no domínio com base em `birth_date`
- O domínio carrega apenas o UUID, sem acessar o aggregate do guardião diretamente

## Matriz de Estados

### `PENDING` (estado inicial)
Campos obrigatório:
- `created_at`

Interpretacao:
- usuario criado mas ainda nao confirmado ou verificado
- pode representar pre-cadastro para reserva de vaga
- nao pode ter `Membership` criado enquanto estiver neste estado

### `ACTIVE`
Campos obrigatório:
- `created_at`
- `activated_at`

Interpretacao:
- usuario verificado e operacional
- pode ter `Membership` criado

### `SUSPENDED`
Campos obrigatório:
- `created_at`
- `suspended_at`
- 
Interpretacao:
- bloqueio temporario da conta (ex: conta comprometida, pendencia administrativa)
- os `Membership` associados nao mudam de estado, mas o acesso e negado pela camada de autorizacao que verifica `User.state` antes de permitir qualquer operacao via `Membership`

### `INACTIVE`
Campos obrigatório:
- `created_at`
- `inactivated_at`

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

Campos obrigatório do `UserTransition`:
- `from_state` — estado anterior
- `to_state` — estado resultante
- `occurred_at` — timestamp da transicao (UTC)
- `actor_id` — quem executou a transicao
- `justification` — justificativa, quando aplicavel

## Responsabilidades da Application
- Validar unicidade de `(identity_type, identity_number, identity_issuer)` antes de criar o `User`
- Validar que `guardian_id` esta presente para usuarios menores de 18 anos
- Validar que o `User` esta em estado `ACTIVE` antes de criar um `Membership`
- Conectar o `User` de domínio ao `auth.User` do Django via `UserModel`

## Plano de Implementacao
- Definir `UserState` enum com `PENDING`, `ACTIVE`, `SUSPENDED`, `INACTIVE`
- Definir `LegalIdentityType` enum com `CPF`, `CERTIDAO_NASCIMENTO`, `PASSPORT`, `CPF`, `CNH`, ´CNI´, `RG`.
- Implementar VO `LegalIdentity` com validacao de `identity_issuer`
- Implementar aggregate `User` com factory method `create()`
- Implementar `UserTransition` Value Object
- Implementar caso de uso `CadastrarUsuario`
- Implementar caso de uso `AtivarUsuario`
- Atualizar pre-condicao de `VincularUsuarioAInstituicaoEPapel`: exigir `User` em `ACTIVE`

## Checklist de Implementação
- [x] Aggregate `User` com todos os campos definidos neste ADR
- [ ] VO `LegalIdentity` com validação de tipo e emissor
- [X] `UserState` enum com quatro estados
- [x] `UserTransition` Value Object implementado
- [x] Factory method `User.create()` nasce em `PENDING`
- [x] Validação de `guardian_id` obrigatório para menores delegada para o domínio
- [ ] Chave de negocio `(identity_type, identity_number)` com constraint no banco
- [ ] `UserModel` carrega FK para `auth.User` do Django

## Checklist de Code Review
- [ ] O domínio nao referencia `auth.User` nem detalhes do Django
- [ ] `birth_date` e imutavel apos criacao
- [ ] `guardian_id` nao e acessado como objeto — apenas como UUID
- [ ] Transicoes proibidas lancam erros de domínio, nao excecoes genericas

## Checklist de Testes
- [ ] Existem testes de criacao de `User` em estado `PENDING`
- [ ] Existem testes de transicao para cada aresta permitida
- [ ] Existem testes de invariante para cada transicao proibida
- [ ] Existem testes de `LegalIdentity` para cada tipo de documento
- [ ] Existe teste de negacao: `Membership` nao pode ser criado para `User` em `PENDING`

## Checklist de Documentacao
- [x] Use cases `CadastrarUsuario`, `AtivarUsuario` e `DesbloquearUsuario` documentados
- [x] Pre-condicao de `VincularUsuarioAInstituicaoEPapel` atualizada para exigir `User ACTIVE`
- [x] ADR 020 atualizado para referenciar este ADR como detalhamento do aggregate `User`
