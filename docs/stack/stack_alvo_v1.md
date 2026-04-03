# Stack Alvo V1

## Objetivo
Definir a stack recomendada para a primeira versao operacional do SaaS escolar com foco em coerencia arquitetural, produtividade e baixo retrabalho.

## Principios
- aproveitar a base tecnica ja existente
- evitar troca de eixo desnecessaria no backend
- priorizar stack conhecida, estavel e bem documentada
- preparar multi-tenancy, API, reporting e operacao sem hipercomplexidade precoce

## Backend
- Python 3.12
- Django 5.2 LTS
- Django REST Framework
- django-filter
- Pydantic apenas onde fizer sentido para DTOs externos ou integracoes, sem disputar o papel do dominio

## Arquitetura Backend
- DDD leve/modular
- Application como orquestradora de casos de uso
- ports and adapters
- camada HTTP fina
- read models dedicados para reporting quando necessario

## Banco e Dados
- PostgreSQL como banco principal
- Redis para cache, rate limiting e apoio a filas/tarefas
- armazenamento S3-compatible para arquivos, exportacoes e boletins em PDF

## Assincrono e Jobs
- Celery para jobs assincronos
- Redis como broker inicial
- tarefas tipicas:
  - exportacoes pesadas
  - emissao de boletins
  - consolidacoes agendadas
  - notificacoes futuras

## Frontend
- React
- TypeScript
- Vite
- TanStack Query
- Tailwind CSS

## Interface e UX
- SPA administrativa no inicio
- portal do estudante e responsavel sobre a mesma stack
- contratos HTTP estaveis e claros

## Qualidade
- pytest
- pytest-django
- pytest-cov
- Ruff
- Pyright
- Vitest no frontend
- Playwright para fluxo E2E critico

## DevOps
- Docker para desenvolvimento e deploy
- GitHub Actions para CI/CD
- deploy em plataforma com suporte a containers
- banco e redis gerenciados quando possivel

## Observabilidade
- Sentry para erro e diagnostico
- OpenTelemetry para tracing e metricas quando o projeto amadurecer
- logs estruturados desde o inicio

## Seguranca
- autenticacao centralizada
- membership institucional por tenant
- controle de permissao por papel e escopo
- auditoria minima para operacoes sensiveis

## Porque esta stack
- conversa com a base atual do projeto
- minimiza troca de tecnologia no backend
- da um caminho claro para API, painel, boletim e relatorios
- segura bem um SaaS escolar de pequeno a medio porte
