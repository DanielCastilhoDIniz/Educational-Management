# Caso de Uso - Reativar Matricula

## Objetivo
Trazer uma matricula de `suspended` para `active`, preservando auditoria e justificativa da reativacao.

## Atores
- secretaria autorizada
- sistema autorizado

## Entrada Conceitual
- `enrollment_id`
- `actor_id`
- `justification`
- `occurred_at` opcional

## Pre-condicoes
- matricula existe
- estado atual e `suspended`
- justificativa obrigatoria
- ator autorizado
- politicas externas permitem reativacao

## Fluxo Principal
1. Carregar aggregate.
2. Validar autorizacao e politicas aplicaveis.
3. Executar comando `reactivate`.
4. Persistir snapshot e transition atomicamente.
5. Retornar resultado estavel.

## Fluxos Alternativos
- matricula nao encontrada
- estado invalido para reativacao
- justificativa ausente
- conflito de concorrencia
- falha tecnica de persistencia

## Pos-condicoes
- `state = active`
- `reactivated_at` preenchido
- `suspended_at` limpo no snapshot atual
- log de transicao atualizado
