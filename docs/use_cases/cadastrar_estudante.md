# Caso de Uso - Cadastrar Estudante

## Objetivo
Registrar um estudante no tenant institucional com dados cadastrais e operacionais minimos.

## Atores
- secretaria
- administrador institucional

## Entrada Conceitual
- dados pessoais
- identificadores institucionais
- contatos basicos
- instituicao alvo

## Pre-condicoes
- ator autorizado
- tenant informado
- unicidade conforme politica de cadastro

## Fluxo Principal
1. Validar autorizacao.
2. Verificar duplicidade cadastral.
3. Criar registro de estudante.
4. Registrar auditoria.
5. Retornar identificador do estudante.
