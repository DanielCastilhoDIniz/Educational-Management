# Caso de Uso - Vincular Usuario a Instituicao e Papel

## Objetivo
Associar um `User` existente a uma instituição com um papel definido, criando o vínculo institucional (`Membership`) em estado inicial `SUSPENDED`. O `Membership` só se torna operacional após execução de `AtivarMembership`.

---

## Atores
| Ator                      | Contexto de uso                                              |
| :------------------------ | :----------------------------------------------------------- |
| `administrador_plataforma` | Vinculação irrestrita, qualquer instituição                 |
| `gestao_executiva`         | Vinculação restrita ao próprio tenant                       |

---

## Entrada Conceitual
| Campo            | Obrigatório | Observação                                                      |
| :--------------- | :---------- | :-------------------------------------------------------------- |
| `user_id`        | sim         | Identificador do `User` a vincular                              |
| `institution_id` | sim         | Identificador da instituição                                    |
| `role_id`        | sim         | Papel a ser atribuído ao vínculo                                |
| `course_id`      | condicional | Obrigatório quando o `Role` exige escopo de curso               |
| `actor_id`       | sim         | Ator que executa a operação — registrado em `created_by`        |
| `occurred_at`    | não         | Timestamp da operação; usa UTC server time se ausente           |

---

## Pré-condições
- Ator autenticado e com papel autorizado para este caso de uso.
- `User` existe e `User.state == ACTIVE`.
- `Institution` existe no sistema.
- `Role` existe e pertence à instituição ou à plataforma.
- `course_id` existe, quando informado.

---

## Fluxo Principal
1. Ator envia os dados do vínculo.
2. Sistema valida autorização do ator.
3. Sistema verifica que `User.state == ACTIVE`.
4. Sistema busca o `Role` pelo `role_id` e verifica se `course_id` é obrigatório para esse papel.
5. Sistema verifica que não existe vínculo com a mesma chave `(user_id, institution_id, course_id)` em estado `ACTIVE` ou `SUSPENDED`.
6. Sistema gera o `registration_code` conforme a política da instituição.
7. Sistema instancia o aggregate `Membership` em estado `SUSPENDED`.
8. Sistema registra o evento de domínio `MembershipCreated`.
9. Sistema persiste o snapshot inicial.
10. Sistema retorna o `membership_id` e o estado `SUSPENDED`.

---

## Fluxos Alternativos

### FA-01: Ator não autorizado (passo 2)
- Condição: ator não possui papel com escopo para vincular usuários.
- Resultado: operação rejeitada imediatamente.
- Código: `AUTHORIZATION_DENIED`

### FA-02: Usuário não encontrado ou inativo (passo 3)
- Condição: `user_id` não existe ou `User.state != ACTIVE`.
- Resultado: operação rejeitada.
- Código: `POLICY_VIOLATION`

### FA-03: Referência inválida (passo 4)
- Condição: `institution_id`, `role_id` ou `course_id` não existe no sistema.
- Resultado: operação rejeitada.
- Código: `POLICY_VIOLATION`

### FA-04: Role incompatível com course_id (passo 4)
- Condição: papel exige `course_id` mas não foi informado, ou vice-versa.
- Resultado: operação rejeitada.
- Código: `POLICY_VIOLATION`

### FA-05: Vínculo duplicado ativo (passo 5)
- Condição: já existe `Membership` com a mesma chave em estado `ACTIVE` ou `SUSPENDED`.
- Resultado: operação rejeitada.
- Código: `DUPLICATE_MEMBERSHIP`

### FA-06: Vínculo inativo encontrado (passo 5)
- Condição: já existe `Membership` com a mesma chave em estado `INACTIVE`.
- Resultado: operação rejeitada; orientar para caso de uso de revinculação.
- Código: `MEMBERSHIP_INACTIVE_CONFLICT`

### FA-07: Colisão de registration_code (passo 9)
- Condição: constraint de unicidade do banco rejeita o `registration_code` gerado.
- Resultado: falha de persistência traduzida para erro de integridade.
- Código: `DATA_INTEGRITY_ERROR`

---

## Taxonomia de Erros

| Código                      | Categoria    | Descrição                                                        |
| :-------------------------- | :----------- | :--------------------------------------------------------------- |
| `AUTHORIZATION_DENIED`      | Autorização  | Ator não possui escopo para vincular usuários                    |
| `POLICY_VIOLATION`          | Negócio      | Referência inválida ou regra de papel/escopo violada             |
| `DUPLICATE_MEMBERSHIP`      | Negócio      | Vínculo ativo ou suspenso já existe para a mesma chave           |
| `MEMBERSHIP_INACTIVE_CONFLICT` | Negócio   | Vínculo inativo encontrado — revinculação requer caso de uso dedicado |
| `DATA_INTEGRITY_ERROR`      | Técnico      | Colisão de `registration_code` na persistência                   |

---

## Pós-condições
- `Membership` existe em persistência com estado `SUSPENDED`.
- `role_id` preenchido.
- `registration_code` gerado e imutável.
- `created_at` preenchido (UTC).
- `created_by` preenchido com `actor_id`.
- `activated_at = null`.
- Evento `MembershipCreated` registrado no buffer do aggregate.

---

## Políticas Consultadas
- [Política de Autorização e Matriz de Atores](../policies/politica_autorizacao_e_matriz_de_atores.md) — valida atores e escopos para este caso de uso.
- [ADR 020 - Identidade, Acesso e Membership Institucional](../adr/020-identity-access-and-membership.md) — decisão de separação entre `User` e `Membership`.
- [ADR 031 - Design do Aggregate Membership](../adr/031-membership-aggregate-design.md) — campos, chave de negócio, `registration_code` e estados do `Membership`.
- [ADR 032 - Design do Aggregate User](../adr/032-user-aggregate-design.md) — exigência de `User.state == ACTIVE` para criação de `Membership`.

---

## Observações
- `course_id` não é apenas dado de transporte — faz parte da chave de negócio `(user_id, institution_id, course_id)`.
- O `Membership` nasce `SUSPENDED`: o acesso só é liberado após `AtivarMembership`.
- Vínculos `INACTIVE` não podem ser reativados por este caso de uso — existe um caso de uso dedicado.
- A emissão de `MembershipCreated` e o consumo downstream são responsabilidade de outros contextos.
