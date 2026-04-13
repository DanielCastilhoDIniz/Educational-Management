# Matriz de Filtros para Relatorios e Consultas

## Objetivo
Padronizar filtros que podem ser reutilizados em relatorios, boletins e dashboards.

## Filtros Comuns
- `institution_id`
- `unit_id`, se existir
- `school_year_id`
- `period_id`
- `class_group_id`
- `subject_id`
- `teacher_id`
- `student_id`
- `enrollment_id`
- `date_from`
- `date_to`
- `report_status` (`partial`, `official`, `closed`, `pending`)

## Filtros Especificos de Frequencia
- percentual minimo de frequencia
- situacao de frequencia
- somente estudantes abaixo do limite
- somente aulas com ausencia registrada

## Filtros Especificos de Aulas
- aulas com frequencia nao lancada
- aulas com diario incompleto
- aulas por professor
- aulas por disciplina

## Filtros Especificos de Notas e Desempenho
- abaixo da media
- acima da media
- pendencia de nota
- disciplina especifica
- avaliacao especifica

## Regras de UX e Contrato
- filtros devem ser composicionais
- datas devem respeitar politica de UTC e timezone de exibicao
- ordenacao deve ser explicita
- exportacao deve refletir exatamente os filtros aplicados
- o contrato de API deve retornar metadados de pagina, total e criterios usados
