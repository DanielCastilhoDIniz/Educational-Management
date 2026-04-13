# Matriz Ator x Caso de Uso x Escopo

## Objetivo
Definir, em nivel operacional, quem pode executar quais casos de uso e dentro de qual escopo.

## Campos da Matriz
- ator
- caso de uso
- tenant
- escopo adicional
- permitido
- observacoes

## Matriz Inicial Resumida

### Secretaria
- criar matricula: permitido no proprio tenant
- suspender/reativar/cancelar matricula: permitido no proprio tenant, conforme politica
- cadastrar estudante/responsavel/professor: permitido no proprio tenant
- emitir boletim oficial: permitido se a politica permitir

### Coordenacao
- concluir matricula: permitido conforme politica
- fechar periodo: permitido
- emitir relatorios gerenciais: permitido
- registrar aula: normalmente nao, salvo fluxo corretivo autorizado

### Professor
- registrar aula: permitido apenas em atribuicoes proprias
- lancar frequencia: permitido apenas em atribuicoes proprias
- lancar notas: permitido apenas em atribuicoes proprias e dentro da janela
- relatorios: apenas em escopos proprios quando a politica permitir

### Responsavel
- consultar boletim: apenas de estudantes vinculados
- consultar painel do estudante: apenas de estudantes vinculados
- relatorios gerenciais: nao permitido

### Estudante
- consultar painel proprio: permitido
- consultar boletim proprio: permitido conforme politica
- relatorios administrativos: nao permitido

### Sistema
- fechamento de periodo: permitido quando configurado
- emissao automatica de boletim: permitido quando autorizado
- rotinas de consolidacao e integracao: permitido conforme fluxo documentado

## Recomendacao
Esta matriz deve futuramente ser quebrada em tabelas por contexto e tambem alimentar testes de autorizacao.
