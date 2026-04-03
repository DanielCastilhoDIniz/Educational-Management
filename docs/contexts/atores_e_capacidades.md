# Atores e Capacidades do Produto

## Atores Principais
- administrador da plataforma
- administrador institucional
- secretaria
- coordenacao
- professor
- responsavel
- estudante
- sistema
- integracao autorizada

## Capacidades por Ator

### Administrador da Plataforma
- governar tenants e operacao global
- suporte e observabilidade cross-tenant sob controles fortes

### Administrador Institucional
- configurar estrutura academica
- gerenciar usuarios e papeis da instituicao
- definir politicas locais dentro do permitido

### Secretaria
- cadastrar estudantes, responsaveis e professores
- criar turmas, periodos e matriculas
- operar cancelamentos, suspensoes e regularizacoes

### Coordenacao
- acompanhar diario, avaliacao e consolidacao academica
- autorizar excecoes pedagogicas quando permitido

### Professor
- registrar aulas
- lancar frequencia
- criar avaliacoes dentro da politica
- lancar notas

### Responsavel
- consultar dados permitidos do estudante
- acompanhar frequencia e boletim quando liberado

### Estudante
- consultar dados permitidos de sua vida academica

### Sistema
- executar rotinas automaticas como fechamento, integracao e notificacoes

## Observacao
Autorizacao real deve combinar ator, tenant, escopo institucional e caso de uso.
