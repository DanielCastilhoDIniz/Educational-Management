# Caso de Uso - Suspender Membership

## Objetivo
Bloquear temporariamente o vínculo de um `User` com uma instituição específica, transitando o `Membership` de `ACTIVE` para `SUSPENDED`. Diferente de `SuspenderUsuario`, afeta apenas uma instituição — o `User` e os demais `Membership` permanecem inalterados. Suporta dois contextos: suspensão por decisão administrativa (`direcao_estrategica`) e suspensão por inadimplência (`gestao_financeira`).

---

## Atores
| Ator                   | Contexto de uso                                                         |
| :--------------------- | :---------------------------------------------------------------------- |
| `direcao_estrategica`  | Suspensão por decisão administrativa ou disciplinar                     |
| `gestao_financeira`    | Suspensão por inadimplência — único papel autorizado para este motivo   |

---

## Entrada Conceitual
| Campo           | Obrigatório | Observação                                                         |
| :-------------- | :---------- | :----------------------------------------------------------------- |
| `membership_id` | sim         | Identificador do `Membership` a suspender                          |
| `reason`        | sim         | Justificativa obrigatória — registrada no `MembershipTransition`   |

---

## Pré-condições
- Ator autenticado e com papel autorizado para este caso de uso.
- `Membership` existe no sistema.
- `Membership.state == ACTIVE`.
- `target.institution_id == actor.membership.institution_id` (exceto `administrador_plataforma`).

---

## Fluxo Principal
1. Ator envia o `membership_id` e a justificativa `reason`.
2. Sistema valida se o ator possui autorização para este caso de uso e se o escopo é válido.
3. Sistema busca o `Membership` pelo `membership_id`.
4. Sistema valida que `Membership.state == ACTIVE`.
5. Sistema executa a transição `ACTIVE → SUSPENDED` e registra `MembershipTransition` com `actor_id`, `occurred_at` e `reason`.
6. Sistema retorna o novo estado do `Membership`.

---

## Fluxos Alternativos

### FA-01: Ator não autorizado
- Condição: ator não possui papel com escopo para suspender memberships.
- Resultado: operação rejeitada imediatamente.
- Código: `AUTHORIZATION_DENIED`

### FA-02: Membership não encontrado
- Condição: não existe `Membership` com o `membership_id` informado.
- Resultado: operação rejeitada.
- Código: `MEMBERSHIP_NOT_FOUND`

### FA-03: Estado inválido para transição
- Condição: `Membership.state != ACTIVE`.
- Resultado: operação rejeitada; estado atual é retornado para orientar o ator.
- Código: `INVALID_STATE_TRANSITION`

---

## Taxonomia de Erros

| Código                     | Categoria   | Descrição                                                      |
| :------------------------- | :---------- | :------------------------------------------------------------- |
| `AUTHORIZATION_DENIED`     | Autorização | Ator não possui escopo para suspender memberships              |
| `MEMBERSHIP_NOT_FOUND`     | Busca       | Nenhum `Membership` encontrado com o `membership_id` informado |
| `INVALID_STATE_TRANSITION` | Negócio     | `Membership` não está em estado `ACTIVE`                       |

---

## Pós-condições
- `Membership.state == SUSPENDED`.
- `MembershipTransition` registrado com `from_state = ACTIVE`, `to_state = SUSPENDED`, `actor_id`, `occurred_at` e `reason`.
- Um evento de domínio `MembershipSuspended` está disponível para consumo downstream.
- O `User` e os demais `Membership` permanecem inalterados.

---

## Políticas Consultadas
- [Política de Autorização e Matriz de Atores](../policies/politica_autorizacao_e_matriz_de_atores.md)
- [ADR 031 - Design do Aggregate Membership](../adr/031-membership-aggregate-design.md)

---

## Observações
- A separação de atores reflete separação de deveres: o motivo financeiro pertence exclusivamente à `gestao_financeira`, evitando interferência da direção em decisões de caixa.
- Para bloquear o acesso em todas as instituições, use `SuspenderUsuario`.
- O desbloqueio após inadimplência é realizado via `AtivarMembership` pela `gestao_financeira`.
