# Caso de Uso - Vincular Usuario a Instituicao e Papel

## Objetivo
Associar um usuario existente a uma instituicao com papel e escopos operacionais.

## Atores
- administrador da plataforma
- administrador institucional

## Entrada Conceitual
- `user_id`
- `institution_id`
- papel
- escopos adicionais
- data de vigencia, quando aplicavel

## Pre-condicoes
- usuario existe
- instituicao existe
- ator autorizado
- papel valido segundo a matriz institucional

## Fluxo Principal
1. Validar permissao.
2. Verificar se o vinculo ja existe.
3. Criar membership institucional.
4. Registrar auditoria.
5. Retornar contrato estavel.
