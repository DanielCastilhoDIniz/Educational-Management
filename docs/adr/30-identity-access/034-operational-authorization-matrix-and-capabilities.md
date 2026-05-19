# ADR 034 - Matriz Operacional de Autorizacao com Capabilities Explicitas

## Status
Aprovado

## Contexto
O ADR 033 estabeleceu o design do aggregate `Role` e introduziu o conceito de `Capability` como Value Object estatico no dominio. Este ADR formaliza o contrato operacional completo: quais capabilities existem, como sao nomeadas e como se relacionam com os casos de uso documentados na politica de autorizacao.

O documento de politica (`politica_autorizacao_e_matriz_de_atores.md`) e a fonte de verdade para as regras de negocio. A coluna `Capability requerida` da Secao 4 e o elo entre a politica e o codigo — cada linha da matriz com um caso de uso atual corresponde a uma entrada no `Capability` StrEnum do dominio.

## Decisao
Formalizar a Matriz de Autorizacao Operacional como o unico mecanismo de derivacao do catalogo de `Capabilities`. Nenhum valor pode ser adicionado ao `Capability` StrEnum sem uma linha correspondente e aprovada na matriz.

## Principios de Design

### Matriz-Primeiro (Matrix-First)
A matriz precede o codigo. Qualquer nova operacao no sistema deve primeiro ser documentada como um caso de uso na matriz (com ator, alvo, escopo, condicao e capability), e somente depois traduzida para uma entrada no StrEnum.

### Um caso de uso unico = uma Capability
Quando o mesmo caso de uso aparece em multiplas linhas com atores diferentes, isso representa uma capability unica. Os atores diferentes determinam quem pode usa-la — nao quantas capabilities existem.

### Convencao de nomenclatura: `recurso:acao`
O valor serializado de cada `Capability` segue o formato `recurso:acao` em letras minusculas (ex: `enrollment:create`, `grade:record`). O recurso e o aggregate afetado. A acao descreve o que acontece com ele.

### Casos de uso futuros
Linhas marcadas como `(futuro)` na matriz documentam extensao esperada. As capabilities correspondentes nao entram no StrEnum ate que o caso de uso seja promovido — quando o modulo e implementado e o ADR correspondente aprovado.

### Principals tecnicos (Service Accounts)
`sistema` e `integracao_autorizada` nao instanciam `Role` via aggregate institucional. Recebem um conjunto tecnico explicito de `Capabilities` por contrato (ex: configuracao de deployment ou token scope). A verificacao de capability para esses atores segue o mesmo pipeline de validacao, mas por mecanismo proprio — sem consultar a tabela `Role`.

## Catalogo de Capabilities Ativas

| Constante | Valor serializado | Caso de Uso na Matriz |
| :--- | :--- | :--- |
| `USER_CREATE` | `user:create` | Cadastrar Usuario |
| `USER_ACTIVATE` | `user:activate` | Ativar Usuario |
| `USER_UNLOCK` | `user:unlock` | Desbloquear Usuario |
| `USER_SUSPEND` | `user:suspend` | Suspender Usuario |
| `USER_CLOSE` | `user:close` | Encerrar Usuario |
| `MEMBERSHIP_CREATE` | `membership:create` | Vincular Usuario a Instituicao |
| `MEMBERSHIP_ACTIVATE` | `membership:activate` | Ativar Membership |
| `MEMBERSHIP_SUSPEND` | `membership:suspend` | Suspender Membership |
| `MEMBERSHIP_CLOSE` | `membership:close` | Encerrar Membership |
| `INSTITUTION_CREATE` | `institution:create` | Cadastrar Instituicao |
| `INSTITUTION_CONFIGURE` | `institution:configure` | Configurar Instituicao |
| `NETWORK_STRUCTURE_CREATE` | `network_structure:create` | Cadastrar Rede, Instituicao e Unidade |
| `STUDENT_CREATE` | `student:create` | Cadastrar Estudante |
| `TEACHER_CREATE` | `teacher:create` | Cadastrar Professor |
| `GUARDIAN_CREATE` | `guardian:create` | Cadastrar Responsavel e Vincular ao Estudante |
| `ENROLLMENT_CREATE` | `enrollment:create` | Criar Matricula |
| `ENROLLMENT_READ` | `enrollment:read` | Consultar Matricula |
| `ENROLLMENT_HISTORY_READ` | `enrollment_history:read` | Listar Historico de Matricula |
| `ENROLLMENT_SUSPEND` | `enrollment:suspend` | Suspender Matricula |
| `ENROLLMENT_REACTIVATE` | `enrollment:reactivate` | Reativar Matricula |
| `ENROLLMENT_CANCEL` | `enrollment:cancel` | Cancelar Matricula |
| `SCHOOL_YEAR_CREATE` | `school_year:create` | Criar Ano Letivo e Periodos |
| `CLASS_GROUP_CREATE` | `class_group:create` | Criar Turma |
| `TEACHER_ASSIGN` | `teacher:assign` | Associar Professor a Disciplina e Turma |
| `LESSON_RECORD` | `lesson:record` | Registrar Aula |
| `ATTENDANCE_RECORD` | `attendance:record` | Lancar Frequencia |
| `GRADE_RECORD` | `grade:record` | Lancar Avaliacao e Notas |
| `PERIOD_CLOSE` | `period:close` | Fechar Periodo e Calcular Media |
| `GRADEBOOK_STUDENT_READ` | `gradebook_student:read` | Consultar Boletim do Estudante |
| `DASHBOARD_STUDENT_READ` | `dashboard_student:read` | Consultar Painel do Estudante |
| `REPORT_OFFICIAL_ISSUE` | `report:official_issue` | Emitir Boletim Oficial |
| `REPORT_READ` | `report:read` | Emitir Relatorio (leitura) |
| `REPORT_EXPORT` | `report:export` | Emitir Relatorio (exportacao) |

## Catalogo de Capabilities Futuras (nao implementadas)

Documentadas na matriz com marcacao `(futuro)`. Nao entram no StrEnum ate promocao.

| Constante | Valor serializado | Caso de Uso na Matriz |
| :--- | :--- | :--- |
| `USER_IDENTITY_VALIDATE` | `user:validate_identity` | Validar Doc. Civil |
| `MEMBERSHIP_TRANSFER` | `membership:transfer` | Trancar ou Transferir |
| `MEMBERSHIP_ROLE_CHANGE` | `membership:role_change` | Trocar Papel de Membership |
| `CERTIFICATE_ISSUE` | `certificate:issue` | Emitir Certificado |
| `CURRICULUM_CREATE` | `curriculum:create` | Criar Grade Curricular |
| `LESSON_APPROVE` | `lesson:approve` | Aprovar Diario de Classe |
| `GRADE_AUDIT` | `grade:audit` | Auditar Notas |
| `ROLE_CREATE` | `role:create` | Criar Role |
| `ROLE_DEACTIVATE` | `role:deactivate` | Desativar Role |
| `ROLE_ACTIVATE` | `role:activate` | Reativar Role |
| `POLICY_CONFIGURE` | `policy:configure` | Configurar Politica Institucional |

## Decisoes Registradas

### ENROLLMENT_CONCLUDE — removida
A conclusao de matricula e sempre acionada por criterios de dominio (fechamento de periodo, cumprimento de requisitos curriculares) — nunca por comando direto de um ator. Portanto nao e uma capability de autorizacao. A transicao de estado e responsabilidade do dominio quando `PERIOD_CLOSE` e executado. A capability `PERIOD_CLOSE` cobre a autorizacao suficiente para esse fluxo.

### TEACHER_ASSIGN — consolidada
A linha futura "Alocar Professor" era redundante com a linha atual "Associar Professor a Disciplina e Turma". Ambas representam a mesma operacao com o mesmo escopo. A linha futura foi removida da matriz. A capability `TEACHER_ASSIGN` permanece ativa e unica.

## Consequencias

### Positivas
- Rastreabilidade bidirecional: de qualquer capability no codigo e possivel chegar a linha da matriz que a justifica, e vice-versa
- Nenhuma capability orfã no StrEnum — todo valor tem uma regra de negocio documentada
- Capabilities futuras sao visiveis e nomeadas antes de existirem no codigo, facilitando planejamento

### Negativas / Riscos
- A matriz, este ADR e o StrEnum precisam ser mantidos em sincronismo — divergencia entre os tres gera autorizacao incorreta em runtime sem erro de compilacao

## Checklist de Manutencao
- [ ] Ao adicionar nova capability: documentar linha na matriz primeiro, depois atualizar este catalogo e o StrEnum
- [ ] Ao promover caso de uso de futuro para atual: mover da tabela de futuras para a ativa e adicionar ao StrEnum
- [ ] Ao renomear capability: atualizar matriz, este ADR e StrEnum simultaneamente
- [ ] Resolver decisoes pendentes antes de implementar `ENROLLMENT_CONCLUDE` e `TEACHER_ASSIGN`
- [ ] Revisao semestral junto ao documento de politica de autorizacao
