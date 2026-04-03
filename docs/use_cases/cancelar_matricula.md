# Caso de Uso - Cancelar Matricula

## Objetivo
Encerrar uma matricula por cancelamento com justificativa auditavel.

## Atores
- secretaria autorizada
- suporte administrativo autorizado
- sistema, quando houver regra institucional explicita

## Entrada Conceitual
- `enrollment_id`
- `actor_id`
- `justification`
- `occurred_at` opcional

## Pre-condicoes
- matricula existe
- estado atual permite cancelamento
- justificativa obrigatoria
- ator autorizado
- politicas externas nao bloqueiam a operacao

## Fluxo Principal
1. Carregar aggregate.
2. Validar autorizacao e politicas externas.
3. Executar comando `cancel`.
4. Persistir snapshot e transition atomicamente.
5. Retornar resultado estavel.

## Fluxos Alternativos
- matricula nao encontrada
- estado invalido para cancelamento
- justificativa ausente
- conflito de concorrencia
- erro tecnico de integridade

## Pos-condicoes
- `state = cancelled`
- `cancelled_at` preenchido
- matricula torna-se terminal
