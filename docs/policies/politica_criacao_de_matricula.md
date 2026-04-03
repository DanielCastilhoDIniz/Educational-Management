# Politica - Criacao de Matricula

## Objetivo
Definir quando uma matricula nova pode ser criada e qual chave de negocio deve ser protegida contra duplicidade.

## Escopo
Aplicada pela Application antes da criacao do aggregate e reforcada por persistencia quando possivel.

## Regras Sugeridas
- matricula so pode ser criada para estudante, turma e periodo validos
- deve existir janela institucional de criacao ou excecao autorizada
- chave de unicidade de negocio sugerida: `student_id + class_group_id + academic_period_id`
- criacao fora da janela exige justificativa institucional e autoridade especifica, se esse caminho for permitido
- criacao automatica deve ser claramente auditada como execucao de sistema

## Resultado Esperado
A politica deve responder, no minimo:
- permitido ou nao
- motivos da decisao
- necessidade de justificativa
- metadados para auditoria

## Testes Recomendados
- criacao dentro da janela
- criacao fora da janela
- duplicidade detectada
- duplicidade nao detectada
- excecao institucional autorizada
