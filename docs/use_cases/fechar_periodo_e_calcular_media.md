# Caso de Uso - Fechar Periodo e Calcular Media

## Objetivo
Consolidar frequencia, notas e media de um periodo letivo para uma turma, disciplina ou estudante, conforme a granularidade adotada.

## Atores
- coordenacao
- sistema
- administrador institucional, quando autorizado

## Entrada Conceitual
- `period_id`
- escopo de consolidacao
- `actor_id`

## Pre-condicoes
- periodo elegivel para fechamento
- politicas congeladas e resolvidas
- dados minimos de frequencia e nota disponiveis
- ator autorizado

## Fluxo Principal
1. Validar autorizacao.
2. Resolver politicas de media e frequencia.
3. Consolidar resultados.
4. Persistir resultado do periodo.
5. Registrar auditoria.
6. Retornar resumo do fechamento.
