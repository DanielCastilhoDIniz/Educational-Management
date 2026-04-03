# Caso de Uso - Consultar Boletim do Estudante

## Objetivo
Exibir ao ator autorizado o boletim do estudante com notas, frequencia e consolidado disponivel.

## Atores
- secretaria
- coordenacao
- responsavel
- estudante
- sistema

## Entrada Conceitual
- `student_id` ou `enrollment_id`
- periodo ou ano letivo
- `actor_id`

## Pre-condicoes
- ator autorizado
- estudante/matricula existe
- dados consolidados ou parciais disponiveis conforme politica de visibilidade

## Fluxo Principal
1. Validar autorizacao.
2. Carregar dados de notas, frequencia e medias.
3. Aplicar politica de visibilidade.
4. Retornar contrato de leitura estavel.
