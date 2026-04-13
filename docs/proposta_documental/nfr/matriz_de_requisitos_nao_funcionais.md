# Matriz de Requisitos Nao Funcionais

## Objetivo
Registrar requisitos nao funcionais minimos do SaaS escolar para orientar arquitetura, deploy e operacao.

## Categorias

### Disponibilidade
- disponibilidade alvo por ambiente
- tolerancia a indisponibilidade em horarios criticos

### Performance
- latencia alvo para APIs transacionais
- latencia alvo para consultas de dashboard
- tempo maximo esperado para exportacoes sincronas

### Escala
- quantidade estimada de instituicoes
- volume estimado de estudantes, turmas e lancamentos
- volume esperado de relatorios e exportacoes

### Consistencia
- quais dados exigem leitura fortemente consistente
- onde dado parcial e aceitavel

### Recuperacao
- RPO e RTO desejados
- politica de backup e restore

### Seguranca
- autenticacao obrigatoria
- segregacao por tenant
- auditoria de operacoes sensiveis

### Compliance e Privacidade
- retencao de dados
- mascaramento
- exportacao e rastreabilidade
