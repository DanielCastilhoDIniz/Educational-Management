# Caso de Uso - Criar Ano Letivo e Periodos

## Objetivo
Configurar o ano letivo institucional e seus periodos de acordo com a politica da instituicao.

## Atores
- administrador institucional
- secretaria com permissao ampliada

## Entrada Conceitual
- `institution_id`
- ano de referencia
- lista de periodos
- datas e metadados de vigencia

## Pre-condicoes
- ator autorizado
- nao haver conflito com estrutura academica existente
- periodos validos segundo a politica institucional

## Fluxo Principal
1. Validar autorizacao.
2. Validar politica de calendario.
3. Criar ano letivo.
4. Criar periodos associados.
5. Registrar auditoria.
6. Retornar estrutura criada.
