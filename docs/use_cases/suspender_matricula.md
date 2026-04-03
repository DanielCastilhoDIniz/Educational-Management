# Caso de Uso - Suspender Matricula

## Objetivo
Mover uma matricula do estado `active` para `suspended` com justificativa e trilha de auditoria.

## Atores
- secretaria autorizada
- sistema autorizado por politica

## Entrada Conceitual
- `enrollment_id`
- `actor_id`
- `justification`
- `occurred_at` opcional

## Pre-condicoes
- matricula existe
- estado atual e `active`
- justificativa obrigatoria
- ator autorizado
- politicas externas permitem suspensao

## Fluxo Principal
1. Carregar aggregate.
2. Validar autorizacao e politicas externas.
3. Executar comando de dominio `suspend`.
4. Persistir snapshot e transition na mesma transacao.
5. Retornar resultado estavel com eventos do dominio.

## Fluxos Alternativos
- matricula nao encontrada
- estado invalido para suspensao
- justificativa ausente
- conflito de concorrencia
- erro tecnico de integridade

## Pos-condicoes
- `state = suspended`
- `suspended_at` preenchido
- nova transicao append-only registrada
