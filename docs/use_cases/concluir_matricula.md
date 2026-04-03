# Caso de Uso - Concluir Matricula

## Objetivo
Encerrar uma matricula por conclusao academica quando a politica institucional considerar o estudante elegivel.

## Atores
- secretaria autorizada
- sistema ao final do periodo, quando aplicavel

## Entrada Conceitual
- `enrollment_id`
- `actor_id`
- `verdict` de elegibilidade
- `justification` quando exigida
- `occurred_at` opcional

## Pre-condicoes
- matricula existe
- estado atual e `active`
- politica de conclusao retorna permissao
- justificativa e obrigatoria quando o verdict exigir
- ator autorizado

## Fluxo Principal
1. Carregar aggregate.
2. Resolver politicas externas de elegibilidade.
3. Executar comando `conclude`.
4. Persistir snapshot e transition na mesma transacao.
5. Retornar resultado estavel com eventos gerados.

## Fluxos Alternativos
- matricula nao encontrada
- matricula nao ativa
- verdict nao permite conclusao
- justificativa obrigatoria ausente
- conflito de concorrencia
- falha tecnica de persistencia

## Pos-condicoes
- `state = concluded`
- `concluded_at` preenchido
- matricula torna-se terminal
