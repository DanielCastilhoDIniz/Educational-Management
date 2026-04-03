# Caso de Uso - Listar Historico de Matricula

## Objetivo
Recuperar o historico append-only de transicoes de uma matricula em ordem cronologica para auditoria, suporte ou visao administrativa.

## Atores
- secretaria
- coordenacao
- suporte autorizado
- sistema

## Entrada Conceitual
- `enrollment_id`
- `actor_id`
- filtros opcionais de periodo e pagina, quando aplicavel

## Pre-condicoes
- matricula existente
- ator autorizado a consultar trilha de auditoria

## Fluxo Principal
1. Validar autorizacao.
2. Carregar log de transicoes do aggregate.
3. Ordenar por `occurred_at` e criterio secundario deterministico, se necessario.
4. Retornar lista estavel de fatos de transicao.

## Fluxos Alternativos
- matricula nao encontrada
- ator sem permissao
- log inconsistente com snapshot atual deve ser sinalizado para suporte

## Pos-condicoes
- operacao somente leitura
- nenhum evento novo publicado
