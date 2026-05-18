# ADR 033 - Design do Aggregate Role

## Status
Proposto

## Contexto
O ADR 020 estabeleceu que papéis e escopos pertencem ao `Membership` institucional, não ao `User` global. Para viabilizar essa separação, o sistema precisa de um catálogo de papéis disponíveis — entidades que definem *o que um ator pode fazer* dentro de uma instituição.

O documento de política (`politica_autorizacao_e_matriz_de_atores.md`) define uma hierarquia explícita de 5 níveis (0–4) com 11 atores possíveis. A matriz de autorização usa essa hierarquia para validar permissões — por exemplo, a `secretaria` só pode criar usuários com papel de nível inferior ao seu.

Este ADR define as decisões de design do aggregate `Role`.

## Decisão
Modelar `Role` como aggregate root responsável pelo catálogo de papéis do sistema.
`Role` é um conceito do sistema — independente de qualquer usuário ou instituição. O vínculo entre um `User`, um `Role` e uma `Institution` é responsabilidade do aggregate `Membership`.

## Campos do Aggregate

| Campo        | Tipo     | Obrigatório | Imutável | Descrição                                                        |
|--------------|----------|-------------|----------|------------------------------------------------------------------|
| `id`         | UUID     | sim         | sim      | identificador técnico do papel                                   |
| `name`       | string   | sim         | não      | nome legível do papel (ex: "Professor", "Secretaria")            |
| `code`       | string   | sim         | sim      | código de política de acesso (ex: `professor`, `secretaria`)     |
| `level`      | int      | sim         | sim      | nível hierárquico (0–4) conforme taxonomia de atores             |
| `status`     | enum     | sim         | não      | estado atual do papel (`ACTIVE` ou `INACTIVE`)                   |
| `created_by` | string   | sim         | sim      | audit trail — quem criou o papel (normalmente `administrador_plataforma`) |
| `created_at` | datetime | sim         | sim      | timestamp de criação (UTC)                                       |

## Chave de Negócio
`code` é único no sistema. Não podem existir dois `Role` com o mesmo `code`.

## Hierarquia de Níveis

Baseada na taxonomia da política de autorização:

| Nível | Código(s)                                              | Descrição                        |
|-------|--------------------------------------------------------|----------------------------------|
| 0     | `administrador_plataforma`                             | Superusuário cross-tenant        |
| 1     | `direcao_estrategica`, `gestao_financeira`             | Estratégico institucional        |
| 2     | `secretaria`, `coordenacao`, `suporte_adm`             | Operacional interno              |
| 3     | `professor`                                            | Execução curricular              |
| 4     | `estudante`, `responsavel`                             | Utilizador final                 |

Atores automatizados (`sistema`, `integracao_autorizada`) são identificados por mecanismo próprio (service account) e não instanciam `Role` via este aggregate.

O `administrador_plataforma` (nível 0) é identificado pelo sinalizador `is_superuser` do Django auth e não possui `Membership`. A existência de um `Role` de nível 0 no catálogo é opcional — sua autoridade é verificada antes da checagem de `Role`.

## Matriz de Estados

### `ACTIVE` (estado inicial)
- Papel disponível para ser referenciado em novos `Membership`
- Campos obrigatórios: `created_at`

### `INACTIVE`
- Papel desativado — não pode ser referenciado em novos `Membership`
- **Soft-Deprecation**: `Membership` já existentes com este papel **não são afetados automaticamente**. Quem já possui o vínculo continua operando até ser revisado manualmente pela instituição.
- A camada de autorização lê o `Role.code` cacheado no `Membership` ou no token JWT — não realiza JOIN na tabela `Role` a cada requisição. Isso garante performance, mas significa que a desativação de um papel não bloqueia imediatamente os usuários com `Membership` existentes.
- Estado reversível: pode ser reativado

## Transições Permitidas
- `ACTIVE → INACTIVE` (desativar papel)
- `INACTIVE → ACTIVE` (reativar papel)

## Transições Proibidas
- Qualquer outra combinação de estados

## Registro de Transições
`Role` não mantém histórico de transições. O snapshot com o estado atual é suficiente dado que:
- Há apenas dois estados possíveis
- Não há dados ricos na transição (sem justificativa obrigatória, sem ator rastreado além do `created_by`)
- O aggregate é simples e estável por natureza

## Invariantes
- `code` não pode ser vazio
- `name` não pode ser vazio
- `level` deve estar entre 0 e 4 inclusive — valores fora desse intervalo levantam erro de domínio
- `code` deve ser único no sistema — o domínio dita a regra; a infraestrutura (unique constraint no banco) funciona como última linha de defesa. A unicidade deve ser coordenada pela camada de application (ex: verificação via `RoleRepository.exists_by_code`) antes da persistência.
- `code` e `level` são imutáveis após criação

## Consequências

### Positivas
- Hierarquia explícita no dado — validações de nível não precisam de mapeamento hardcoded na application
- `code` imutável garante estabilidade das referências na política de autorização
- Audit trail via `created_by` — rastreável quem criou cada papel no sistema
- Autorização ultra-rápida (Soft-Deprecation) — zero JOINs extras por requisição; `Role.code` é lido do `Membership` ou do token JWT sem consultar a tabela `Role`

### Negativas / Riscos
- Papéis pré-definidos devem ser criados via seed/migration — o sistema não funciona sem eles
- Soft-Deprecation implica inconsistência temporária: desativar um papel não bloqueia imediatamente usuários com `Membership` existentes — a limpeza de vínculos é responsabilidade da `direcao_estrategica`
- Nomes de papel são globais — se uma instituição preferir um nome diferente (ex: "Escritório de Atendimento" em vez de "Secretaria"), o `name` no `Role` global mudaria para todas as instituições. Mitigação futura: `Membership` ou `ConfiguracaoInstitucional` pode fazer override do nome exibido, mantendo `Role.code` intocado para as regras de autorização.

## Plano de Implementação
- Definir `RoleStatus` enum com `ACTIVE` e `INACTIVE`
- Implementar aggregate `Role` com factory method `create()`
- Implementar erros de domínio: `InvalidStateTransitionError`, `CodeRequiredError`, `NameRequiredError`
- Implementar eventos de domínio: `RoleCreated`, `RoleDeactivated`, `RoleReactivated` — os eventos `RoleDeactivated` e `RoleReactivated` devem carregar `updated_by` (ID do ator que executou a transição) para suportar audit trail em logs e ferramentas de observabilidade, mesmo que o aggregate não persista esse campo no snapshot
- Implementar testes de domínio: invariantes, transições, factory method
- Criar seed com os papéis pré-definidos da taxonomia

## Checklist de Implementação
- [ ] `RoleStatus` enum com `ACTIVE` e `INACTIVE`
- [ ] Aggregate `Role` com campos definidos neste ADR
- [ ] Factory method `Role.create()` nasce em `ACTIVE`
- [ ] Métodos `deactivate()` e `reactivate()` com validação de transição
- [ ] `code` e `level` imutáveis após criação
- [ ] Erros de domínio para transições inválidas e campos obrigatórios

## Checklist de Code Review
- [ ] `Role` não referencia `User` nem `Membership` — é independente
- [ ] `code` e `level` são imutáveis (sem setter, sem mutação interna)
- [ ] Transições inválidas levantam erros de domínio, não exceções genéricas
- [ ] `created_by` é imutável após criação

## Checklist de Testes
- [ ] Criação com campos válidos nasce em `ACTIVE`
- [ ] Tentativa de criar com `code` vazio levanta erro
- [ ] Tentativa de criar com `name` vazio levanta erro
- [ ] `deactivate()` a partir de `ACTIVE` — happy path
- [ ] `reactivate()` a partir de `INACTIVE` — happy path
- [ ] Transição inválida levanta `InvalidStateTransitionError`
- [ ] Tentativa de criar com `level` fora do intervalo 0–4 levanta erro de domínio
