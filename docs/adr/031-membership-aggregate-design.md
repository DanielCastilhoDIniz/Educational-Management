# ADR 031 - Design do Aggregate Membership

## Status
Proposto

## Contexto
O sistema precisa representar o vinculo entre um usuario e uma instituicao, incluindo papel, escopos, estado operacional e codigo de registro legivel. O ADR 020 estabeleceu a separacao conceitual entre identidade global (`Usuario`) e vinculo institucional (`Membership`). Este ADR define as decisoes de design do aggregate `Membership`.

## Decisao
Modelar `Membership` como aggregate root responsavel pelo ciclo de vida do vinculo institucional.

## Campos do Aggregate

| Campo               | Tipo     | Obrigatorio | Imutavel | Descricao                                             |
|---------------------|----------|-------------|----------|-------------------------------------------------------|
| `id`                | UUID     | sim         | sim      | identidade tecnica do vinculo                         |
| `user_id`           | UUID     | sim         | sim      | referencia ao `Usuario` global                        |
| `institution_id`    | UUID     | sim         | sim      | referencia a instituicao (contexto Organizacional)    |
| `course_id`         | UUID     | nao         | sim      | referencia ao curso (contexto Organizacional)         |
| `role_id`           | UUID     | sim         | nao      | referencia ao aggregate `Role`                        |
| `registration_code` | string   | sim         | sim      | codigo legivel gerado no ingresso                     |
| `state`             | enum     | sim         | nao      | estado atual do vinculo                               |
| `created_by`        | string   | sim         | sim      | audit trail da criacao                                |
| `created_at`        | datetime | sim         | sim      | timestamp de criacao                                  |
| `activated_at`      | datetime | nao         | nao      | timestamp da ultima ativacao, null se nunca ativado   |
| `suspended_at`      | datetime | nao         | nao      | timestamp da ultima suspensao, null se nunca suspenso |
| `deactivated_at`    | datetime | nao         | nao      | timestamp de desativacao definitiva                   |
| `expires_at`        | datetime | nao         | nao      | data de expiracao para vinculos temporarios           |

## Regra sobre expires_at
`expires_at` e um campo informativo. A chegada da data de expiracao **nao** dispara mudanca automatica de estado no aggregate. A responsabilidade de monitorar vinculos proximos do vencimento e gerar alertas pertence a um job agendado na infraestrutura, fora do dominio.

## Chave de Negocio
Unicidade garantida por `(user_id, institution_id, course_id)`.

- Para vinculos sem curso (professores, diretores): `course_id = null`
- A validacao de obrigatoriedade do `course_id` e responsabilidade da camada de Application, com base no `Role` do vinculo

## Aggregate Role

`Role` e um aggregate proprio, separado do `Membership`.

Tipos:
- **System Role**: definido pela plataforma, imutavel, sem `institution_id`
- **Custom Role**: criado pela instituicao, contem `institution_id`

Cada `Role` define a colecao de escopos que lhe pertence. O `Membership` referencia `role_id` e nao carrega escopos diretamente.

## Matriz de Estados

### `SUSPENDED` (estado inicial)
Campos obrigatorios:
- `created_at`

Campos permitidos:
- `suspended_at` pode ser `null` (criacao inicial) ou preenchido (retorno de estado `ACTIVE`)
- `activated_at` pode ser `null` (nunca ativado) ou preenchido (ja foi ativo)

Campos proibidos:
- `deactivated_at`

### `ACTIVE`
Campos obrigatorios:
- `created_at`
- `activated_at`

Campos proibidos:
- `deactivated_at`

### `INACTIVE`
Campos obrigatorios:
- `created_at`
- `deactivated_at`

Campos permitidos:
- `activated_at` pode ser `null` (nunca foi ativado) ou preenchido
- `suspended_at` pode ser `null` ou preenchido

## Transicoes Permitidas
- `SUSPENDED -> ACTIVE` (ativacao do vinculo)
- `ACTIVE -> SUSPENDED` (bloqueio temporario: licenca, pendencia administrativa)
- `SUSPENDED -> ACTIVE` (reativacao apos bloqueio)
- `ACTIVE -> INACTIVE` (encerramento definitivo)
- `SUSPENDED -> INACTIVE` (encerramento sem reativacao)

## Transicoes Proibidas
- qualquer transicao a partir de `INACTIVE`
- `SUSPENDED -> SUSPENDED`
- `ACTIVE -> ACTIVE` como operacao de negocio

## Registro de Transicoes
Cada transicao de estado e registrada por um `MembershipTransition` (Value Object), aplicando o mesmo padrao do `StateTransition` do aggregate `Enrollment`. O `Membership` mantem uma colecao interna de transicoes persistida separadamente do snapshot.

Campos obrigatorios do `MembershipTransition`:
- `from_state` — estado anterior
- `to_state` — estado resultante
- `occurred_at` — timestamp da transicao (UTC)
- `actor_id` — quem executou a transicao
- `role_id` — papel vigente no momento da transicao (captura o historico em caso de troca de papel)
- `reason` — justificativa, quando aplicavel

## registration_code
- Gerado no momento da criacao do vinculo
- Imutavel apos a criacao
- Formato definido pela instituicao, recomendado: `{ano_ingresso}{codigo_instituicao}{codigo_papel}{sequencial}`
- Serve como identificador legivel para o usuario em contextos de servico
- Nao e usado como chave tecnica nem como foreign key

## Fluxo Feliz — Vincular Usuario a Instituicao

1. Ator autorizado solicita vinculo com `user_id`, `institution_id`, `course_id` (opcional), `role_id`
2. Application busca o `Role` pelo `role_id` e verifica se `course_id` e obrigatorio para esse papel
3. Application verifica que nao existe vinculo ativo com a mesma chave `(user_id, institution_id, course_id)`
4. Application gera o `registration_code` conforme a politica da instituicao
5. Application chama `Membership.create()` com os dados ja validados
6. O aggregate nasce em estado `SUSPENDED` e registra o evento `MembershipCreated` em memoria
7. Application entrega o aggregate ao repositorio
8. Repositorio persiste o snapshot em transacao atomica
9. Apos confirmacao do save, a infraestrutura publica o evento `MembershipCreated` para rastreabilidade

## Responsabilidades da Application
- Validar se `course_id` e obrigatorio para o `Role` informado antes de criar o `Membership`
- Verificar se o vinculo `(user_id, institution_id, course_id)` ja existe
- Gerar o `registration_code` conforme a politica da instituicao
- Autorizar o ator antes de criar ou alterar o vinculo

## Riscos e Decisoes Pendentes

- **Limbo do SUSPENDED**: vinculos criados e nunca ativados ficam bloqueando o acesso do usuario. O evento `MembershipCreated` deve ser consumido por um contexto de notificacao que alerte o responsavel pela ativacao. Essa responsabilidade esta fora do dominio do `Membership`.
- **Concorrencia na unicidade**: a verificacao de duplicidade na Application pode sofrer race condition em alta carga. A constraint `(user_id, institution_id, course_id)` no banco e a ultima linha de defesa e deve ser garantida.
- **Troca de papel**: o caso de uso `TrocarPapel` ainda nao foi documentado. Deve exigir `actor_id`, registrar `MembershipTransition` com o `role_id` anterior, e ser auditavel.

## Plano de Implementacao
- Definir `MembershipState` enum com `SUSPENDED`, `ACTIVE`, `INACTIVE`
- Implementar aggregate `Membership` com factory method `create()`
- Implementar `MembershipTransition` Value Object
- Implementar aggregate `Role` com tipos `SYSTEM` e `CUSTOM`
- Implementar caso de uso `VincularUsuarioAInstituicaoEPapel`
- Implementar caso de uso `AtivarMembership`
- Documentar use cases de suspensao e encerramento

## Checklist de Implementacao
- [ ] Aggregate `Membership` com todos os campos definidos neste ADR
- [ ] `MembershipState` enum com tres estados
- [ ] `MembershipTransition` Value Object implementado
- [ ] Factory method `Membership.create()` gera `registration_code` e nasce em `SUSPENDED`
- [ ] Aggregate `Role` com tipos `SYSTEM` e `CUSTOM`
- [ ] Validacao de `course_id` obrigatorio delegada para a Application
- [ ] Chave de negocio `(user_id, institution_id, course_id)` com constraint no banco

## Checklist de Code Review
- [ ] `role_id` e imutavel apos criacao ou ha um caso de uso explicito para troca de papel
- [ ] `registration_code` nao e alterado em nenhum metodo do aggregate
- [ ] Transicoes proibidas lancam erros de dominio, nao excecoes genericas
- [ ] A Application nao repassa `course_id` null sem verificar o `Role`

## Checklist de Testes
- [ ] Existem testes de criacao de `Membership` em estado `SUSPENDED`
- [ ] Existem testes de transicao para cada aresta permitida
- [ ] Existem testes de invariante para cada transicao proibida
- [ ] Existem testes de `Membership` sem `course_id` para papeis institucionais
- [ ] Existem testes de `Role` com tipos `SYSTEM` e `CUSTOM`

## Checklist de Documentacao
- [ ] Use cases `VincularUsuarioAInstituicaoEPapel` e `AtivarMembership` documentados
- [ ] Matriz de estados publicada na documentacao de contexto
- [ ] ADR 020 atualizado para referenciar este ADR como detalhamento do aggregate
