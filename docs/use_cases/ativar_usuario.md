# Caso de Uso - Ativar Usuário

## Objetivo
Confirmar a identidade de um `User` recém-cadastrado, transitando seu estado de `PENDING` para `ACTIVE`. Após a ativação, o usuário pode ter um `Membership` criado e ser vinculado a uma instituição.

---

## Atores
| Ator                      | Contexto de uso                                              |
| :------------------------ | :----------------------------------------------------------- |
| `administrador_plataforma` | Ativação irrestrita, qualquer `User`                        |
| `direcao_estrategica`         | Ativação de usuários do próprio tenant                      |

---

## Entrada Conceitual
| Campo     | Obrigatório | Observação                         |
| :-------- | :---------- | :--------------------------------- |
| `user_id` | sim         | Identificador do `User` a ativar   |

---

## Pré-condições
- Ator autenticado e com papel autorizado para este caso de uso.
- `User` existe no sistema.
- `User.state == PENDING`.

---

## Fluxo Principal
1. Ator envia o `user_id` do usuário a ser ativado.
2. Sistema valida se o ator possui autorização para executar este caso de uso.
3. Sistema busca o `User` pelo `user_id`.
4. Sistema valida que `User.state == PENDING`.
5. Sistema executa a transição `PENDING → ACTIVE` e registra `UserTransition` com `actor_id` e `occurred_at`.
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
- Condição: `User.state != PENDING`.
- Resultado: operação rejeitada; estado atual é retornado para orientar o ator.
- Código: `INVALID_STATE_TRANSITION`

---

## Taxonomia de Erros

| Código                   | Categoria    | Descrição                                              |
| :----------------------- | :----------- | :----------------------------------------------------- |
| `AUTHORIZATION_DENIED`   | Autorização  | Ator não possui escopo para ativar usuários            |
| `USER_NOT_FOUND`         | Busca        | Nenhum `User` encontrado com o `user_id` informado     |
| `INVALID_STATE_TRANSITION` | Negócio    | `User` não está em estado `PENDING`                    |

---

## Pós-condições
- `User.state == ACTIVE`.
- `UserTransition` registrado com `from_state = PENDING`, `to_state = ACTIVE`, `actor_id` e `occurred_at`.
- Um evento de domínio `UserActivated` está disponível para consumo downstream.
- O `User` agora pode ter um `Membership` criado.

---

## Políticas Consultadas
- [Política de Autorização e Matriz de Atores](../policies/politica_autorizacao_e_matriz_de_atores.md) — valida quais atores podem ativar usuários.
- [ADR 032 - Design do Aggregate User](../adr/032-user-aggregate-design.md) — define a transição `PENDING → ACTIVE` e o `UserTransition`.

---

## Observações
- A ativação confirma que a identidade foi verificada por um ator responsável — não é um processo automático.
- Após a ativação, o próximo passo natural é `VincularUsuarioAInstituicaoEPapel`.
