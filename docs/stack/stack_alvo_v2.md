# Stack Alvo V2

## Objetivo
Descrever a evolucao recomendada da stack quando o produto entrar em fase de crescimento, carga maior e operacao multi-tenant mais madura.

## Evolucoes Esperadas

### Backend
- manter Python + Django + DRF
- amadurecer a separacao command/query
- introduzir mais read models dedicados
- consolidar outbox e integracoes externas

### Dados
- PostgreSQL continua como fonte primaria
- Redis continua para cache e broker
- considerar replicacao de leitura ou tuning dedicado para consultas pesadas
- ampliar storage para arquivos e exportacoes oficiais

### Assincrono e Eventos
- Celery segue como motor de jobs
- outbox transacional para entrega de eventos
- consumidores idempotentes
- filas separadas por prioridade, quando necessario

### Frontend
- manter React + TypeScript
- avaliar Next.js apenas se surgirem necessidades fortes de SSR, edge rendering ou portal publico com SEO relevante
- fortalecer design system e acessibilidade

### Observabilidade
- OpenTelemetry mais completo
- dashboards operacionais por tenant
- alertas para concorrencia, exportacao, boletim e jobs pendentes

### Segurança e Governanca
- trilha de auditoria mais rica
- classificacao formal de dados
- politicas de retencao e exportacao mais maduras
- endurecimento de controle de acesso e service accounts

### Deploy
- containerizacao continua
- pode evoluir para orquestracao mais robusta se a carga exigir
- backup, disaster recovery e runbooks formais se tornam obrigatorios

## O que eu nao mudaria cedo
- nao migraria backend para Node/FastAPI apenas por moda
- nao adotaria Kubernetes cedo sem necessidade real
- nao quebraria frontend em microfrontends cedo

## Sinal de que vale migrar para V2
- multiplas instituicoes com uso simultaneo consistente
- relatorios pesados frequentes
- jobs demorados e fila crescente
- necessidade real de observabilidade distribuida
- equipe maior trabalhando em paralelo em mais contextos
