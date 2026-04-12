# Caso de Uso - Cadastrar Responsavel e Vincular ao Estudante

## Objetivo
Registrar um responsavel e associa-lo a um estudante com tipo de relação e prioridade de contato.

## Atores
- secretaria
- administrador institucional

## Entrada Conceitual
- dados do responsavel
- `student_id`
- tipo de responsabilidade
- prioridade de contato
- canais de contato

## Pre-condicoes
- estudante existe
- ator autorizado
- relacao permitida pela politica institucional

## Fluxo Principal
1. Validar autorizacao.
2. Criar ou localizar cadastro do responsavel.
3. Criar vinculo responsavel-estudante.
4. Registrar auditoria.
5. Retornar contrato estavel com o vinculo criado.
