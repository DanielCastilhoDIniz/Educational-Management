# Caso de Uso - Cadastrar Usuário

## Objetivo
Registrar a identidade global mínima de uma pessoa no sistema, criando um `User` em estado `PENDING`. O cadastro representa apenas a identidade — sem credenciais, sem vínculo institucional e sem dados de perfil. A vinculação a uma instituição ocorre em um caso de uso separado (`VincularUsuarioAInstituicaoEPapel`).

---

## Atores
| Ator                      | Contexto de uso                                              |
| :------------------------ | :----------------------------------------------------------- |
| `administrador_plataforma` | Cadastro irrestrito, qualquer identidade                    |
| `gestao_executiva`         | Cadastro de equipe da própria instituição                   |
| `secretaria`               | Cadastro de alunos e responsáveis legais                    |
| `sistema`                  | Cadastro automatizado via contrato do gateway de pagamento  |

---

## Entrada Conceitual
| Campo             | Obrigatório | Observação                                                      |
| :---------------- | :---------- | :-------------------------------------------------------------- |
| `full_name`       | sim         | Nome completo da pessoa                                         |
| `birth_date`      | sim         | Data de nascimento; usada para validar necessidade de guardião |
| `identity_type`   | sim         | Tipo do documento: `CPF`, `CERTIDAO_NASCIMENTO`, `PASSPORT`     |
| `identity_number` | sim         | Número do documento                                             |
| `identity_issuer` | condicional | Obrigatório para `CERTIDAO_NASCIMENTO` e `PASSPORT`             |
| `email`           | não         | Opcional; pode ser ausente para menores de idade                |
| `guardian_id`     | condicional | Obrigatório quando `birth_date` indica menor de 18 anos         |

---

## Pré-condições
- Ator autenticado e com papel autorizado para este caso de uso.
- Não existe `User` com a mesma chave `(identity_type, identity_number)` no sistema.

---

## Fluxo Principal
1. Ator envia os dados da pessoa a ser cadastrada.
2. Sistema valida se o ator possui autorização para executar este caso de uso.
3. Sistema verifica se já existe um `User` com a mesma `(identity_type, identity_number)`.
4. Sistema valida os campos obrigatórios e as regras condicionais:
   - `identity_issuer` presente para `CERTIDAO_NASCIMENTO` e `PASSPORT`.
   - `guardian_id` presente quando `birth_date` indica menor de 18 anos.
5. Sistema cria o `User` em estado `PENDING` com `created_by` registrado.
6. Sistema retorna o `user_id` gerado.

---

## Fluxos Alternativos

### FA-01: Ator não autorizado
- Condição: ator não possui papel com escopo para este caso de uso.
- Resultado: operação rejeitada.
- Código: `AUTHORIZATION_DENIED`

### FA-02: Identidade duplicada
- Condição: já existe um `User` com a mesma `(identity_type, identity_number)`.
- Resultado: operação rejeitada; o `user_id` existente **não** é retornado ao ator.
- Código: `DUPLICATE_USER`

### FA-03: Dados inválidos ou incompletos
- Condição: campo obrigatório ausente, formato inválido, ou `identity_issuer` ausente para tipos que exigem.
- Resultado: operação rejeitada com indicação dos campos inválidos.
- Código: `VALIDATION_ERROR`

### FA-04: Guardião ausente para menor de idade
- Condição: `birth_date` indica pessoa com menos de 18 anos e `guardian_id` não foi informado.
- Resultado: operação rejeitada.
- Código: `GUARDIAN_REQUIRED`

---

## Taxonomia de Erros

| Código                | Categoria     | Descrição                                                    |
| :-------------------- | :------------ | :----------------------------------------------------------- |
| `AUTHORIZATION_DENIED` | Autorização  | Ator não possui escopo para cadastrar usuários               |
| `DUPLICATE_USER`       | Negócio      | Identidade `(identity_type, identity_number)` já registrada  |
| `VALIDATION_ERROR`     | Negócio      | Campos obrigatórios ausentes ou formato inválido             |
| `GUARDIAN_REQUIRED`    | Negócio      | Menor de idade sem `guardian_id` informado                   |

---

## Pós-condições
- Um novo `User` existe no sistema com estado `PENDING`.
- A combinação `(identity_type, identity_number)` está registrada e protegida contra duplicatas.
- `created_by` e `created_at` estão preenchidos com o contexto da operação.
- Um evento de domínio `UserCreated` está disponível para consumo downstream.

---

## Políticas Consultadas
- [Política de Autorização e Matriz de Atores](../policies/politica_autorizacao_e_matriz_de_atores.md) — valida quais atores podem cadastrar usuários e com qual escopo.
- [ADR 032 - Design do Aggregate User](../adr/032-user-aggregate-design.md) — define campos, chave de negócio, estados e regras do aggregate.

---

## Observações
- Este caso de uso **não** cria credenciais de acesso (`auth.User`). Autenticação é responsabilidade de um caso de uso específico de ativação.
- Este caso de uso **não** vincula o usuário a nenhuma instituição. O vínculo ocorre em `VincularUsuarioAInstituicaoEPapel`.
- O estado `PENDING` permite reserva de vaga antes de confirmação de identidade.
- Um `User` em estado `PENDING` **não pode** ter `Membership` criado.
- A escolha de não retornar o `user_id` existente no FA-02 é intencional: evita enumeração de identidades cadastradas.
