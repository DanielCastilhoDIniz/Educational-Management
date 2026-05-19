# Sugestao de Catalogo de Capabilities

## Objetivo
Sugerir um catalogo inicial de `Capability` para fechar a lacuna entre:

- a politica de autorizacao e matriz de atores
- o ADR 033 de design do aggregate `Role`

Este documento nao e normativo. Ele serve como proposta de convergencia para:

- nomenclatura
- granularidade
- relacao entre `Role.code` e `Capability`
- limites entre RBAC e predicados de escopo/atributo

## Referencias
- [Politica de Autorizacao e Matriz de Atores](../policies/politica_autorizacao_e_matriz_de_atores.md)
- [ADR 033 - Design do Aggregate Role](../adr/30-identity-access/033-role-aggregate-design.md)
- [ADR 020 - Identidade, Acesso e Membership Institucional](../adr/30-identity-access/020-identity-access-and-membership.md)

## Principios

### 1. Capability autoriza operacao, nao garante execucao isoladamente
Uma `Capability` habilita uma familia de operacoes.
Ela nao substitui:

- validacao de tenant
- estado de `User` e `Membership`
- predicado por `course_id`
- janelas temporais
- politicas institucionais
- verificacao de nivel hierarquico

Exemplo:
- `USER_CREATE` permite iniciar o caso de uso de cadastro
- ainda assim, a policy pode exigir que `secretaria` so crie papeis de nivel inferior

### 2. Formato canonico
Usar o formato:

- nome do enum: `RESOURCE_ACTION`
- valor serializado: `"resource:action"`

Exemplo:

```python
ENROLLMENT_CREATE = "enrollment:create"
```

### 3. Capabilities devem ser estaveis e sem ambiguidades
Preferir recursos do dominio e verbos curtos e consistentes.

### 4. Capabilities representam comandos e consultas relevantes
Nao e necessario criar capability para cada detalhe de implementacao interna.

## Convencoes de Nomenclatura

### Recursos
Preferir nomes no singular:

- `user`
- `membership`
- `role`
- `institution`
- `enrollment`
- `lesson`
- `attendance`
- `grade`
- `period`
- `report`
- `dashboard`

### Verbos recomendados

- `create`
- `read`
- `list`
- `update`
- `activate`
- `suspend`
- `unlock`
- `close`
- `cancel`
- `conclude`
- `assign`
- `record`
- `approve`
- `audit`
- `configure`
- `export`

### Verbos a evitar quando houver sinonimo mais claro

- evitar `manage`
- evitar `handle`
- evitar `process`
- evitar `do`

## Sugestao de Enum Inicial

```python
from enum import StrEnum


class Capability(StrEnum):
    # Identity and access
    USER_CREATE = "user:create"
    USER_ACTIVATE = "user:activate"
    USER_SUSPEND = "user:suspend"
    USER_UNLOCK = "user:unlock"
    USER_CLOSE = "user:close"
    USER_READ = "user:read"

    MEMBERSHIP_CREATE = "membership:create"
    MEMBERSHIP_ACTIVATE = "membership:activate"
    MEMBERSHIP_SUSPEND = "membership:suspend"
    MEMBERSHIP_CLOSE = "membership:close"
    MEMBERSHIP_READ = "membership:read"
    MEMBERSHIP_ROLE_CHANGE = "membership:role_change"

    ROLE_READ = "role:read"
    ROLE_CREATE = "role:create"
    ROLE_ACTIVATE = "role:activate"
    ROLE_DEACTIVATE = "role:deactivate"

    # Organization
    INSTITUTION_CREATE = "institution:create"
    INSTITUTION_CONFIGURE = "institution:configure"
    INSTITUTION_READ = "institution:read"

    # Enrollment
    ENROLLMENT_CREATE = "enrollment:create"
    ENROLLMENT_READ = "enrollment:read"
    ENROLLMENT_LIST = "enrollment:list"
    ENROLLMENT_SUSPEND = "enrollment:suspend"
    ENROLLMENT_REACTIVATE = "enrollment:reactivate"
    ENROLLMENT_CANCEL = "enrollment:cancel"
    ENROLLMENT_CONCLUDE = "enrollment:conclude"

    # Academic structure and operation
    SCHOOL_YEAR_CREATE = "school_year:create"
    PERIOD_CLOSE = "period:close"
    CLASS_GROUP_CREATE = "class_group:create"
    TEACHER_ASSIGN = "teacher:assign"

    LESSON_RECORD = "lesson:record"
    LESSON_APPROVE = "lesson:approve"

    ATTENDANCE_RECORD = "attendance:record"
    ATTENDANCE_AUDIT = "attendance:audit"

    GRADE_RECORD = "grade:record"
    GRADE_AUDIT = "grade:audit"

    # Reporting and student experience
    REPORT_READ = "report:read"
    REPORT_EXPORT = "report:export"
    REPORT_OFFICIAL_ISSUE = "report:official_issue"

    DASHBOARD_STUDENT_READ = "dashboard_student:read"
    GRADEBOOK_STUDENT_READ = "gradebook_student:read"
```

## Observacoes sobre Granularidade

### `read` vs `list`
Quando fizer sentido separar:

- `read` para consultar um recurso especifico
- `list` para consultas agregadas ou listagens

Exemplo:
- `ENROLLMENT_READ`
- `ENROLLMENT_LIST`

### `activate` vs `unlock`
No dominio atual:

- `User` usa `unlock`
- `Membership` usa `activate`

Sugestao:
- manter a capability alinhada ao nome do caso de uso exposto
- nao forcar homogeneizacao artificial onde o dominio ja escolheu outra linguagem

### `report:official_issue`
Separar emissao de relatorio comum da emissao de documento oficial ajuda a refletir:

- boletim oficial
- certificado
- historico com valor institucional

## Mapeamento Inicial Sugerido por Papel

Este mapeamento e apenas um ponto de partida.
Ele precisa continuar sujeito a:

- escopo por tenant
- predicado por curso
- janelas e politicas externas
- estado do `User`
- estado do `Membership`

### `direcao_estrategica`

- `USER_CREATE`
- `USER_ACTIVATE`
- `USER_UNLOCK`
- `MEMBERSHIP_CREATE`
- `MEMBERSHIP_ACTIVATE`
- `MEMBERSHIP_SUSPEND`
- `MEMBERSHIP_CLOSE`
- `MEMBERSHIP_ROLE_CHANGE`
- `ROLE_READ`
- `INSTITUTION_CONFIGURE`
- `ENROLLMENT_READ`
- `ENROLLMENT_LIST`
- `REPORT_READ`
- `REPORT_EXPORT`
- `DASHBOARD_STUDENT_READ`

### `gestao_financeira`

- `MEMBERSHIP_READ`
- `MEMBERSHIP_SUSPEND`
- `MEMBERSHIP_ACTIVATE`
- `ENROLLMENT_READ`
- `REPORT_READ`

### `secretaria`

- `USER_CREATE`
- `MEMBERSHIP_CREATE`
- `ENROLLMENT_CREATE`
- `ENROLLMENT_READ`
- `ENROLLMENT_LIST`
- `ENROLLMENT_SUSPEND`
- `ENROLLMENT_REACTIVATE`
- `ENROLLMENT_CANCEL`
- `REPORT_OFFICIAL_ISSUE`
- `GRADEBOOK_STUDENT_READ`

### `coordenacao`

- `ENROLLMENT_READ`
- `ENROLLMENT_LIST`
- `PERIOD_CLOSE`
- `TEACHER_ASSIGN`
- `LESSON_APPROVE`
- `ATTENDANCE_AUDIT`
- `GRADE_AUDIT`
- `REPORT_READ`
- `REPORT_EXPORT`
- `REPORT_OFFICIAL_ISSUE`

### `suporte_adm`

- `USER_UNLOCK`
- `ENROLLMENT_READ`
- `ENROLLMENT_LIST`
- `ENROLLMENT_CANCEL`
- `INSTITUTION_CONFIGURE`

### `professor`

- `LESSON_RECORD`
- `ATTENDANCE_RECORD`
- `GRADE_RECORD`
- `ENROLLMENT_READ`

### `estudante`

- `DASHBOARD_STUDENT_READ`
- `GRADEBOOK_STUDENT_READ`

### `responsavel`

- `DASHBOARD_STUDENT_READ`
- `GRADEBOOK_STUDENT_READ`

## Casos Especiais

### `administrador_plataforma`
Sugestao:

- nao tratar como `Role` comum
- manter bypass controlado via `is_superuser`
- opcionalmente mapear todas as capabilities para fins de auditoria e teste

### `sistema`
Sugestao:

- nao modelar como `Role` do catalogo institucional
- tratar como `service principal`
- usar um conjunto tecnico proprio de capabilities

Exemplo de conjunto tecnico:

- `ENROLLMENT_CREATE`
- `PERIOD_CLOSE`
- `REPORT_READ`

Sempre acompanhado de:

- `job_name`
- `execution_id`
- `occurred_at`
- trilha de auditoria reforcada

### `integracao_autorizada`
Sugestao:

- tratar como principal tecnico externo
- capabilities liberadas por contrato de integracao
- sem dependencia de `Membership` humano

## Regras que Devem Ficar Fora do Enum

Estas regras nao devem virar `Capability`:

- `target.institution_id == actor.institution_id`
- `actor.membership.course_id == target.course_id`
- `User.state == ACTIVE`
- `Membership.state == ACTIVE`
- "janela de cancelamento aberta"
- "periodo encerrado"
- "papel do alvo deve ter nivel inferior"

Essas regras sao:

- predicados de escopo
- validacoes de estado
- politicas temporais
- restricoes hierarquicas

## Sugestao de Ordem de Implementacao

1. Fechar o catalogo minimo de `Capability`
2. Definir mapeamento oficial `Role.code -> frozenset[Capability]`
3. Ajustar a policy para referenciar capabilities explicitamente
4. Decidir como `sistema` e `integracao_autorizada` entram no pipeline
5. Criar testes de autorizacao por capability + escopo

## Criterios de Pronto

Considerar a proposta madura quando:

- cada capability tiver nome unico e sem sinonimo concorrente
- cada caso de uso da matriz puder apontar para uma ou mais capabilities
- o mapeamento por papel estiver documentado
- service accounts tiverem contrato proprio definido
- RBAC e ABAC estiverem claramente separados na documentacao
