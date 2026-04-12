# Caso de Uso - Desbloquear Usuário

## Objetivo
Reativar um `User` que se encontra em estado `SUSPENDED`, transitando para `ACTIVE` e restaurando o acesso operacional via todos os `Membership` existentes. Diferente de `AtivarUsuario`, este caso de uso pressupõe histórico — o usuário já possui vínculos, notas e rastro de auditoria.

---

## Atores
| Ator                      | Contexto de uso                                                          |
| :------------------------ | :----------------------------------------------------------------------- |
| `gestao_executiva`         | Caso normal — desbloqueio de usuários do próprio tenant                 |
| `administrador_plataforma` | Intervenção de emergência — quando `gestao_executiva` está indisponível |
| `suporte_adm`              | Com autorização explícita — escopo restrito ao próprio tenant           |

---

## Entrada Conceitual
| Campo     | Obrigatório | Observação                                       |
| :-------- | :---------- | :----------------------------------------------- |
| `user_id` | sim         | Identificador do `User` a desbloquear            |
| `reason`  | sim         | Justificativa do desbloqueio — registrada no `UserTransition` |

---

## Pré-condições
- Ator autenticado e com papel autorizado para este caso de uso.
- `User` existe no sistema.
- `User.state == SUSPENDED`.

---

## Fluxo Principal
1. Ator envia o `user_id` e a justificativa `reason`.
2. Sistema valida se o ator possui autorização para executar este caso de uso.
3. Sistema busca o `User` pelo `user_id`.
4. Sistema valida que `User.state == SUSPENDED`.
5. Sistema executa a transição `SUSPENDED → ACTIVE` e registra `UserTransition` com `actor_id`, `occurred_at` e `reason`.
6. Sistema retorna o novo estado do `User`.

---

## Fluxos Alternativos

### FA-01: Ator não autorizado
- Condição: ator não possui papel com escopo para este caso de uso.
- Resultado: operação rejeitada.
- Código: `AUTHORIZATION_DENIED`

### FA-02: Usuário não encontrado
- Condição: não existe `User` com o `user_id` informado.
- Resultado: operação rejeitada.
- Código: `USER_NOT_FOUND`

### FA-03: Estado inválido para transição
- Condição: `User.state != SUSPENDED`.
- Resultado: operação rejeitada; estado atual é retornado para orientar o ator.
- Código: `INVALID_STATE_TRANSITION`

---

## Taxonomia de Erros

| Código                     | Categoria   | Descrição                                                |
| :------------------------- | :---------- | :------------------------------------------------------- |
| `AUTHORIZATION_DENIED`     | Autorização | Ator não possui escopo para desbloquear usuários         |
| `USER_NOT_FOUND`           | Busca       | Nenhum `User` encontrado com o `user_id` informado       |
| `INVALID_STATE_TRANSITION` | Negócio     | `User` não está em estado `SUSPENDED`                    |

---

## Pós-condições
- `User.state == ACTIVE`.
- `UserTransition` registrado com `from_state = SUSPENDED`, `to_state = ACTIVE`, `actor_id`, `occurred_at` e `reason`.
- Um evento de domínio `UserUnblocked` está disponível para consumo downstream.
- O acesso via todos os `Membership` existentes é restaurado automaticamente pela camada de autorização.

---

## Políticas Consultadas
- [Política de Autorização e Matriz de Atores](../policies/politica_autorizacao_e_matriz_de_atores.md) — valida quais atores podem desbloquear usuários e em quais condições.
- [ADR 032 - Design do Aggregate User](../adr/032-user-aggregate-design.md) — define a transição `SUSPENDED → ACTIVE` e o `UserTransition`.

---

## Observações
- Os `Membership` **não mudam de estado** durante a suspensão nem no desbloqueio. O acesso é negado/restaurado pela camada de autorização que verifica `User.state` antes de qualquer operação.
- A `reason` é obrigatória — o desbloqueio de um usuário suspenso é uma decisão que precisa de rastreabilidade.
- A intervenção do `administrador_plataforma` deve ser usada apenas em emergências e sempre gerará registro de auditoria completo.
