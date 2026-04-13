# Caso de Uso - Ativar Membership

## Objetivo
Ativar um `Membership` que se encontra em estado `SUSPENDED`, transitando para `ACTIVE` e liberando o acesso do usuário na instituição específica. Cobre dois cenários: primeira ativação (após criação via `VincularUsuarioAInstituicaoEPapel`) e reativação (após suspensão operacional). Diferente de `DesbloquearUsuario`, este caso de uso afeta apenas o vínculo com uma instituição — o `User` e os demais `Membership` permanecem inalterados.

---

## Atores
| Ator                      | Contexto de uso                                              |
| :------------------------ | :----------------------------------------------------------- |
| `administrador_plataforma` | Reativação irrestrita, qualquer `Membership`                |
| `direcao_estrategica`         | Ativação de `Membership` do próprio tenant                  |
| `gestao_financeira`           | Reativação após confirmação de pagamento                    |

---

## Entrada Conceitual
| Campo           | Obrigatório | Observação                                                    |
| :-------------- | :---------- | :------------------------------------------------------------ |
| `membership_id` | sim         | Identificador do `Membership` a reativar                      |
| `reason`        | sim         | Justificativa da reativação — registrada na transição de estado |

---

## Pré-condições
- Ator autenticado e com papel autorizado para este caso de uso.
- `Membership` existe no sistema.
- `Membership.state == SUSPENDED`.

---

## Fluxo Principal
1. Ator envia o `membership_id` e a justificativa `reason`.
2. Sistema valida se o ator possui autorização para executar este caso de uso.
3. Sistema busca o `Membership` pelo `membership_id`.
4. Sistema valida que `Membership.state == SUSPENDED`.
5. Sistema executa a transição `SUSPENDED → ACTIVE` e registra `MembershipTransition` com `actor_id`, `occurred_at` e `reason`.
6. Sistema retorna o novo estado do `Membership`.

---

## Fluxos Alternativos

### FA-01: Ator não autorizado
- Condição: ator não possui papel com escopo para este caso de uso.
- Resultado: operação rejeitada.
- Código: `AUTHORIZATION_DENIED`

### FA-02: Membership não encontrado
- Condição: não existe `Membership` com o `membership_id` informado.
- Resultado: operação rejeitada.
- Código: `MEMBERSHIP_NOT_FOUND`

### FA-03: Estado inválido para transição
- Condição: `Membership.state != SUSPENDED`.
- Resultado: operação rejeitada; estado atual é retornado para orientar o ator.
- Código: `INVALID_STATE_TRANSITION`

---

## Taxonomia de Erros

| Código                     | Categoria   | Descrição                                                     |
| :------------------------- | :---------- | :------------------------------------------------------------ |
| `AUTHORIZATION_DENIED`     | Autorização | Ator não possui escopo para reativar memberships              |
| `MEMBERSHIP_NOT_FOUND`     | Busca       | Nenhum `Membership` encontrado com o `membership_id` informado |
| `INVALID_STATE_TRANSITION` | Negócio     | `Membership` não está em estado `SUSPENDED`                   |

---

## Pós-condições
- `Membership.state == ACTIVE`.
- `MembershipTransition` registrado com `from_state = SUSPENDED`, `to_state = ACTIVE`, `actor_id`, `occurred_at` e `reason`.
- Um evento de domínio `MembershipReactivated` está disponível para consumo downstream.
- O acesso do usuário na instituição é liberado; demais `Membership` e o `User` permanecem inalterados.

---

## Políticas Consultadas
- [Política de Autorização e Matriz de Atores](../policies/politica_autorizacao_e_matriz_de_atores.md) — valida quais atores podem reativar memberships.
- [ADR 031 - Design do Aggregate Membership](../adr/031-membership-aggregate-design.md) — define a transição `SUSPENDED → ACTIVE` e o `MembershipTransition`.

---

## Observações
- A suspensão de um `Membership` é cirúrgica: afeta apenas o vínculo com a instituição específica.
- A suspensão de um `User` derruba o acesso em todas as instituições — independente do estado dos `Membership`.
- A `reason` é obrigatória para garantir rastreabilidade da decisão de reativação.
