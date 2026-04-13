# Caso de Uso - Vincular Usuario a Instituicao e Papel

## Objetivo
Associar um usuario existente a uma instituicao com papel e escopos operacionais, gerando o vinculo institucional (`Membership`) em estado inicial `SUSPENDED`.

## Atores
- administrador da plataforma
- administrador institucional

## Entrada Conceitual
- `user_id`
- `institution_id`
- `course_id` (opcional, obrigatorio conforme o papel)
- `role_id`
- `actor_id`
- `occurred_at` opcional

## Regras de Entrada Ja Definidas
- `user_id`, `institution_id` e `role_id` sao obrigatorios
- `course_id` e obrigatorio apenas quando o `Role` exige — validado pela Application
- a chave de negocio do vinculo e `(user_id, institution_id, course_id)`
- o `registration_code` e gerado pela Application conforme a politica da instituicao

## Pre-condicoes
- usuario existe
- `User.state == ACTIVE`
- instituicao existe
- `course_id` existe, quando informado
- ator esta autorizado
- papel valido segundo a matriz institucional

## Fluxo Principal
1. Receber os dados do vinculo.
2. Validar autorizacao do ator.
3. Buscar o `Role` pelo `role_id` e verificar se `course_id` e obrigatorio para esse papel.
4. Verificar que nao existe vinculo com a mesma chave `(user_id, institution_id, course_id)`.
5. Gerar o `registration_code` conforme a politica da instituicao.
6. Instanciar o aggregate `Membership` em estado `SUSPENDED`.
7. Registrar o evento de dominio `MembershipCreated`.
8. Persistir o snapshot inicial.
9. Retornar resultado estavel para a camada superior.

## Fluxos Alternativos

### Ator nao autorizado (passo 2)
- Erro: `AUTHORIZATION_DENIED`
- O caso de uso e interrompido imediatamente.

### Referencia invalida (passo 1)
- `user_id`, `institution_id` ou `course_id` nao existe no sistema.
- Erro: `POLICY_VIOLATION`

### Role incompativel com course_id (passo 3)
- O papel exige `course_id` mas ele nao foi informado, ou vice-versa.
- Erro: `POLICY_VIOLATION`

### Vinculo duplicado ativo (passo 4)
- Ja existe um `Membership` com a mesma chave em estado `ACTIVE` ou `SUSPENDED`.
- Erro: `DUPLICATE_MEMBERSHIP`

### Vinculo inativo encontrado (passo 4)
- Ja existe um `Membership` com a mesma chave em estado `INACTIVE`.
- Erro: `MEMBERSHIP_INACTIVE_CONFLICT`
- Orientacao: use o caso de uso de reativacao de membership.

### Colisao de registration_code (passo 8)
- Constraint de unicidade do banco rejeita o `registration_code` gerado.
- Erro de persistencia traduzido para: `DATA_INTEGRITY_ERROR`

## Estado Atual da Implementacao
- o aggregate `Membership` ainda nao foi implementado
- o service `VincularUsuarioAInstituicaoEPapel` ainda nao existe
- o aggregate `Role` ainda nao foi implementado
- as validacoes de autorizacao, politicas e cadastro mestre dependem dos contextos de usuarios, roles e cadastro organizacional
- este documento descreve o contrato alvo do caso de uso

## Pos-condicoes
- `Membership` existe em persistencia
- `state = SUSPENDED`
- `role_id` preenchido
- `registration_code` gerado e imutavel
- `created_at` preenchido (UTC)
- `created_by` preenchido com `actor_id`
- `activated_at = null`
- evento `MembershipCreated` registrado no buffer do aggregate

## Politicas Consultadas
- politica de autorizacao do ator
- politica de validacao do papel (`course_id` obrigatorio ou nao)
- politica de unicidade do vinculo `(user_id, institution_id, course_id)`
- politica de geracao do `registration_code` (definida pela instituicao, com padrao sugerido pela plataforma)

## Observacoes
- `course_id` nao e apenas um dado de transporte; ele faz parte da chave de negocio do vinculo
- a existencia do contrato nao significa que todas as dependencias de autorizacao e politica ja estejam implementadas
- a emissao de `MembershipCreated` e a rastreabilidade de eventos downstream sao responsabilidades de outros contextos
- vinculos com `INACTIVE` nao podem ser reativados por este caso de uso — existe um caso de uso dedicado para isso
