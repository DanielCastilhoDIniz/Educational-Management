# Caso de Uso - Encerrar Usuário

## Objetivo
Encerrar definitivamente a identidade global de um `User`, transitando para `INACTIVE`. É um estado terminal — sem transições de saída. Por ser uma ação de escopo global e irreversível, é reservada ao `administrador_plataforma`. Após o encerramento, todos os `Membership` existentes ficam inacessíveis e nenhuma nova operação pode ser executada sobre esta identidade.

---

## Atores
| Ator                      | Contexto de uso                                                          |
| :------------------------ | :----------------------------------------------------------------------- |
| `administrador_plataforma` | Único ator autorizado — encerramento global e irreversível               |

---

## Entrada Conceitual
| Campo     | Obrigatório | Observação                                                          |
| :-------- | :---------- | :------------------------------------------------------------------ |
| `user_id` | sim         | Identificador do `User` a encerrar                                  |
| `reason`  | sim         | Justificativa obrigatória — encerramento global é irreversível       |

---

## Pré-condições
- Ator autenticado como `administrador_plataforma`.
- `User` existe no sistema.
- `User.state in (ACTIVE, SUSPENDED)`.

---

## Fluxo Principal
1. Ator envia o `user_id` e a justificativa `reason`.
2. Sistema valida que o ator é `administrador_plataforma`.
3. Sistema busca o `User` pelo `user_id`.
4. Sistema valida que `User.state` é `ACTIVE` ou `SUSPENDED`.
5. Sistema executa a transição para `INACTIVE` e registra `UserTransition` com `actor_id`, `occurred_at` e `reason`.
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
- Condição: `User.state == INACTIVE` (já encerrado) ou `User.state == PENDING`.
- Resultado: operação rejeitada; estado atual é retornado para orientar o ator.
- Código: `INVALID_STATE_TRANSITION`

---

## Taxonomia de Erros

| Código                     | Categoria   | Descrição                                              |
| :------------------------- | :---------- | :----------------------------------------------------- |
| `AUTHORIZATION_DENIED`     | Autorização | Ator não é `administrador_plataforma`                  |
| `USER_NOT_FOUND`           | Busca       | Nenhum `User` encontrado com o `user_id` informado     |
| `INVALID_STATE_TRANSITION` | Negócio     | `User` está em `INACTIVE` ou `PENDING`                 |

---

## Pós-condições
- `User.state == INACTIVE`.
- `UserTransition` registrado com `from_state` anterior, `to_state = INACTIVE`, `actor_id`, `occurred_at` e `reason`.
- Um evento de domínio `UserClosed` está disponível para consumo downstream.
- O acesso via todos os `Membership` existentes fica permanentemente bloqueado pela camada de autorização.
- **Nenhum dado é apagado** — a identidade e o histórico são preservados nativamente.

---

## Políticas Consultadas
- [Política de Autorização e Matriz de Atores](../policies/politica_autorizacao_e_matriz_de_atores.md)
- [ADR 032 - Design do Aggregate User](../adr/032-user-aggregate-design.md)

---

## Observações
- `INACTIVE` é estado terminal — não existe caso de uso de reativação de `User` encerrado.
- Os `Membership` associados **não mudam de estado** — são bloqueados pela camada de autorização que verifica `User.state` antes de qualquer operação.
- Encerramento de `User` em `PENDING` não é permitido — use a transição `PENDING → INACTIVE` apenas quando aplicável pelo domínio; este caso de uso opera sobre identidades já ativas ou suspensas.
- Para encerrar apenas o vínculo com uma instituição específica, use `EncerrarMembership`.
