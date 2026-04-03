# Caso de Uso - Consultar Painel do Estudante

## Objetivo
Exibir ao estudante ou responsavel um painel consolidado com desempenho por disciplina, frequencia e recortes temporais.

## Atores
- estudante
- responsavel
- sistema

## Entrada Conceitual
- `student_id`
- filtros por ano letivo, periodo, disciplina e intervalo de datas
- `actor_id`

## Pre-condicoes
- ator autenticado e autorizado
- estudante vinculado ao ator, quando se tratar de responsavel
- filtros validos

## Fluxo Principal
1. Validar identidade e visibilidade.
2. Carregar metricas do painel no recorte filtrado.
3. Montar a visao geral e os detalhes por disciplina.
4. Identificar claramente dados oficiais e parciais.
5. Retornar contrato de leitura do painel.
