# Mapa de Bounded Contexts Proposto

## Objetivo
Descrever os contextos de negocio esperados para o SaaS e seus pontos de integracao.

## Contextos

### 1. Identidade e Acesso
Responsavel por:
- usuarios
- autenticacao
- memberships por instituicao
- papeis e autorizacoes

### 2. Organizacao Institucional
Responsavel por:
- instituicoes
- unidades, se existirem
- calendarios e parametros institucionais
- configuracoes por tenant

### 3. Cadastro Academico
Responsavel por:
- estudantes
- professores
- responsaveis
- disciplinas
- ano letivo
- periodos
- turmas

### 4. Matriculas
Responsavel por:
- vinculo do estudante a turma/periodo
- estado da matricula
- transicoes de ciclo de vida
- auditoria de mudancas de estado

### 5. Diario de Classe
Responsavel por:
- aulas ministradas
- conteudos
- frequencia
- observacoes pedagogicas operacionais

### 6. Avaliacao e Boletim
Responsavel por:
- avaliacoes
- notas
- medias
- consolidacao por periodo
- boletim e resultado academico

### 7. Auditoria e Operacao
Responsavel por:
- trilhas de auditoria
- logs estruturados
- metricas e alertas
- suporte operacional

## Relacoes Principais
- matricula depende de cadastro academico e organizacao institucional
- diario depende de turma, disciplina, professor e matricula
- avaliacao depende de turma, disciplina, periodo e regime avaliativo
- identidade e acesso corta todos os contextos
- auditoria e operacao observam todos os contextos

## Recomendacao
Cada contexto importante deve ter:
- linguagem ubiqua propria
- casos de uso principais
- politicas externas explicitas
- contratos de persistencia e integracao bem definidos
