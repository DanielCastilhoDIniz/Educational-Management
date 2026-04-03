# Caso de Uso - Emitir Boletim Oficial

## Objetivo
Emitir o boletim oficial do estudante com base em dados consolidados e politicas vigentes no periodo.

## Atores
- secretaria
- coordenacao
- sistema, em fluxo automatizado autorizado

## Entrada Conceitual
- `student_id` ou `enrollment_id`
- `period_id` ou `school_year_id`
- formato de emissao
- `actor_id`

## Pre-condicoes
- ator autorizado
- periodo elegivel ou fechado segundo a politica
- dados consolidados disponiveis

## Fluxo Principal
1. Validar autorizacao e elegibilidade para emissao.
2. Carregar consolidado oficial do estudante.
3. Montar o boletim com notas, medias e frequencia.
4. Registrar versao, data e emissor.
5. Retornar ou disponibilizar o documento.

## Pos-condicoes
- documento emitido e rastreavel
- versao do boletim preservada
- emissao auditavel
