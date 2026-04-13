# Caso de Uso - Suspender Usuário

## Objetivo
Bloquear temporariamente a identidade global de um `User`, transitando de `ACTIVE` para `SUSPENDED`. Por ser uma ação de escopo global — que impede o acesso em todas as instituições — é reservada exclusivamente ao `administrador_plataforma`. A `direcao_estrategica` de uma instituição específica suspende o `Membership`, não o `User`.

---

## Atores
| Ator                      | Contexto de uso                                                        |
| :------------------------ | :--------------------------------------------------------------------- |
| `administrador_plataforma` | Único ator autorizado — suspensão tem efeito cross-tenant              |

---

## Entrada Conceitual
| Campo     | Obrigatório | Observação                                                        |
| :-------- | :---------- | :---------------------------------------------------------------- |
| `user_id` | sim         | Identificador do `User` a suspender                               |
| `reason`  | sim         | Justificativa obrigatória — escopo global exige rastreabilidade   |

---

## Pré-condições
- Ator autenticado como `administrador_plataforma`.
- `User` existe no sistema.
- `User.state == ACTIVE`.

---

## Fluxo Principal
1. Ator envia o `user_id` e a justificativa `reason`.
2. Sistema valida que o ator é `administrador_plataforma`.
3. Sistema busca o `User` pelo `user_id`.
4. Sistema valida que `User.state == ACTIVE`.
5. Sistema executa a transição `ACTIVE → SUSPENDED` e registra `UserTransition` com `actor_id`, `occurred_at` e `reason`.
6. Sistema retorna o novo estado do `User`.

---

## Fluxos Alternativos

### FA-01: Ator não autorizado
- Condição: ator não é `administrador_plataforma`.
- Resultado: operação rejeitada imediatamente.
- Código: `AUTHORIZATION_DENIED`

### FA-02: Usuário não encontrado
- Condição: não existe `User` com o `user_id` informado.
- Resultado: operação rejeitada.
- Código: `USER_NOT_FOUND`

### FA-03: Estado inválido para transição
- Condição: `User.state != ACTIVE`.
- Resultado: operação rejeitada; estado atual é retornado para orientar o ator.
- Código: `INVALID_STATE_TRANSITION`

---

## Taxonomia de Erros

| Código                     | Categoria   | Descrição                                              |
| :------------------------- | :---------- | :----------------------------------------------------- |
| `AUTHORIZATION_DENIED`     | Autorização | Ator não é `administrador_plataforma`                  |
| `USER_NOT_FOUND`           | Busca       | Nenhum `User` encontrado com o `user_id` informado     |
| `INVALID_STATE_TRANSITION` | Negócio     | `User` não está em estado `ACTIVE`                     |

---

## Pós-condições
- `User.state == SUSPENDED`.
- `UserTransition` registrado com `from_state = ACTIVE`, `to_state = SUSPENDED`, `actor_id`, `occurred_at` e `reason`.
- Um evento de domínio `UserSuspended` está disponível para consumo downstream.
- O acesso via todos os `Membership` existentes é bloqueado pela camada de autorização — os `Membership` **não mudam de estado**.

---

## Políticas Consultadas
- [Política de Autorização e Matriz de Atores](../policies/politica_autorizacao_e_matriz_de_atores.md)
- [ADR 032 - Design do Aggregate User](../adr/032-user-aggregate-design.md)

---

## Observações
- Suspensão de `User` é uma ação de plataforma, não institucional — afeta todas as instituições.
- Para bloquear o acesso de um usuário em apenas uma instituição, use `SuspenderMembership`.
- A `reason` é obrigatória e imutável após o registro — não pode ser alterada retroativamente.
