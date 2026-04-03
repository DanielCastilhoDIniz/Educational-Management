# Caso de Uso - Cadastrar Usuario

## Objetivo
Criar uma identidade de usuario que possa futuramente ser vinculada a uma ou mais instituicoes.

## Atores
- administrador da plataforma
- administrador institucional, se a politica permitir

## Entrada Conceitual
- dados basicos de identificacao
- credenciais ou mecanismo de autenticacao adotado
- metadados de contato

## Pre-condicoes
- dados obrigatorios validos
- unicidade conforme politica de identidade
- ator autorizado

## Fluxo Principal
1. Validar permissao.
2. Validar unicidade da identidade.
3. Criar usuario global.
4. Registrar auditoria.
5. Retornar identificador e metadados relevantes.
