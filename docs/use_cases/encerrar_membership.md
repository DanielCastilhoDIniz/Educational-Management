# Caso de Uso - Encerrar Membership

## Objetivo
Encerrar definitivamente o vínculo de um `User` com uma instituição, transitando o `Membership` para `INACTIVE`. É um estado terminal — sem transições de saída. Usado quando o vínculo não deve mais existir operacionalmente (ex: desligamento, transferência definitiva, graduação).

---

## Atores
| Ator                      | Contexto de uso                                              |
| :------------------------ | :----------------------------------------------------------- |
| `direcao_estrategica`     | Encerramento de vínculos do próprio tenant                   |
| `administrador_plataforma` | Encerramento irrestrito, qualquer `Membership`              |

---

## Entrada Conceitual
| Campo           | Obrigatório | Observação                                                         |
| :-------------- | :---------- | :----------------------------------------------------------------- |
| `membership_id` | sim         | Identificador do `Membership` a encerrar                           |
| `reason`        | sim         | Justificativa obrigatória — encerramento é irreversível            |

---

## Pré-condições
- Ator autenticado e com papel autorizado para este caso de uso.
- `Membership` existe no sistema.
- `Membership.state in (ACTIVE, SUSPENDED)`.

---

## Fluxo Principal
1. Ator envia o `membership_id` e a justificativa `reason`.
2. Sistema valida se o ator possui autorização para este caso de uso e se o escopo é válido.
3. Sistema busca o `Membership` pelo `membership_id`.
4. Sistema valida que `Membership.state` é `ACTIVE` ou `SUSPENDED`.
5. Sistema executa a transição para `INACTIVE` e registra `MembershipTransition` com `actor_id`, `occurred_at` e `reason`.
6. Sistema retorna o novo estado do `Membership`.

---

## Fluxos Alternativos

### FA-01: Ator não autorizado
- Condição: ator não possui papel com escopo para encerrar memberships.
- Resultado: operação rejeitada imediatamente.
- Código: `AUTHORIZATION_DENIED`

### FA-02: Membership não encontrado
- Condição: não existe `Membership` com o `membership_id` informado.
- Resultado: operação rejeitada.
- Código: `MEMBERSHIP_NOT_FOUND`

### FA-03: Estado inválido para transição
- Condição: `Membership.state == INACTIVE` (já encerrado).
- Resultado: operação rejeitada; estado atual é retornado para orientar o ator.
- Código: `INVALID_STATE_TRANSITION`

---

## Taxonomia de Erros

| Código                     | Categoria   | Descrição                                                      |
| :------------------------- | :---------- | :------------------------------------------------------------- |
| `AUTHORIZATION_DENIED`     | Autorização | Ator não possui escopo para encerrar memberships               |
| `MEMBERSHIP_NOT_FOUND`     | Busca       | Nenhum `Membership` encontrado com o `membership_id` informado |
| `INVALID_STATE_TRANSITION` | Negócio     | `Membership` já está em estado `INACTIVE`                      |

---

## Pós-condições
- `Membership.state == INACTIVE`.
- `MembershipTransition` registrado com `from_state` anterior, `to_state = INACTIVE`, `actor_id`, `occurred_at` e `reason`.
- Um evento de domínio `MembershipClosed` está disponível para consumo downstream.
- O `User` e os demais `Membership` permanecem inalterados.
- **Nenhum dado é apagado** — o histórico do vínculo é preservado nativamente.

---

## Políticas Consultadas
- [Política de Autorização e Matriz de Atores](../policies/politica_autorizacao_e_matriz_de_atores.md)
- [ADR 031 - Design do Aggregate Membership](../adr/031-membership-aggregate-design.md)

---

## Observações
- `INACTIVE` é estado terminal — não existe caso de uso de reativação de `Membership` encerrado.
- Para vincular novamente o mesmo `User` à mesma instituição após encerramento, é necessário criar um novo `Membership` via `VincularUsuarioAInstituicaoEPapel`.
- O histórico do vínculo anterior é preservado pelo `INACTIVE` existente — não há conflito com a nova criação.
