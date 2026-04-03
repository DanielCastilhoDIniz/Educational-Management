# Politica - Autorizacao e Matriz de Atores

## Objetivo
Definir quem pode executar cada caso de uso e em quais condicoes.

## Atores Sugeridos
- secretaria
- coordenacao
- suporte administrativo
- sistema
- integracao externa autorizada

## Matriz Inicial Sugerida
- criar matricula: secretaria, sistema autorizado
- consultar matricula: secretaria, coordenacao, suporte, sistema autorizado
- listar historico: secretaria, coordenacao, suporte autorizado
- suspender: secretaria autorizada
- reativar: secretaria autorizada
- cancelar: secretaria e suporte administrativo conforme regra
- concluir: secretaria ou sistema ao fim do periodo, conforme politica

## Regras Operacionais
- autorizacao deve ser validada antes do comando de dominio
- service accounts devem ser identificaveis e auditaveis
- negacao de autorizacao deve ter codigo estavel na Application

## Testes Recomendados
- ator autorizado
- ator nao autorizado
- service account permitida
- actor humano sem escopo suficiente
