# Caso de Uso - Cadastrar Professor

## Objetivo
Registrar professor no tenant institucional para futura associacao a disciplinas e turmas.

## Atores
- secretaria
- administrador institucional

## Entrada Conceitual
- dados pessoais
- dados funcionais
- instituicao alvo

## Pre-condicoes
- ator autorizado
- unicidade conforme politica institucional

## Fluxo Principal
1. Validar autorizacao.
2. Verificar duplicidade.
3. Criar cadastro de professor.
4. Registrar auditoria.
5. Retornar identificador do professor.
