# Caso de Uso - Registrar Aula

## Objetivo
Permitir que o professor registre uma aula ministrada com data, horario e conteudo lecionado.

## Atores
- professor
- coordenacao, em fluxo de correcao autorizado

## Entrada Conceitual
- `teacher_assignment_id`
- data/hora da aula
- conteudo
- observacoes opcionais

## Pre-condicoes
- professor associado a turma/disciplina
- ator autorizado
- aula dentro da janela permitida pela politica

## Fluxo Principal
1. Validar autorizacao e atribuicao.
2. Validar janela operacional.
3. Registrar aula.
4. Registrar auditoria.
5. Retornar identificador da aula.
