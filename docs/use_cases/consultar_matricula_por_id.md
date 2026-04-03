# Caso de Uso - Consultar Matricula por ID

## Objetivo
Recuperar o estado atual de uma matricula e seus dados minimos de auditoria para exibicao ou integracao.

## Atores
- secretaria
- coordenacao
- sistema
- integracao autorizada

## Entrada Conceitual
- `enrollment_id`
- `actor_id`
- escopo de visibilidade, quando aplicavel

## Pre-condicoes
- ator autorizado a consultar a matricula
- aggregate existente

## Fluxo Principal
1. Validar autorizacao de leitura.
2. Carregar snapshot atual.
3. Retornar contrato de leitura estavel.
4. Registrar trilha de auditoria de acesso, se aplicavel.

## Fluxos Alternativos
- matricula nao encontrada: retorno estavel de not found
- ator nao autorizado: retorno estavel de autorizacao negada

## Pos-condicoes
- nenhum efeito de mutacao no aggregate
- nenhuma transicao nova persistida

## Observacoes
Este caso de uso e de leitura e nao deve depender do contrato de `save()`.
