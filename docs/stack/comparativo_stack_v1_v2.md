# Comparativo - Stack V1 x Stack V2

## Objetivo
Resumir o que entra ja e o que fica para a fase de escala.

## V1 - Entrar Ja
- Python 3.12
- Django 5.2 LTS
- DRF
- django-filter
- PostgreSQL
- Redis
- Celery
- React
- TypeScript
- Vite
- TanStack Query
- Tailwind CSS
- Docker
- GitHub Actions
- Sentry
- pytest, Ruff, Pyright, Vitest, Playwright

## V2 - Entrar Quando Houver Pressao Real
- outbox transacional completo
- read models mais sofisticados
- observabilidade com OpenTelemetry madura
- segregacao maior de filas
- estrategia de escala de leitura/reporting
- eventuais evolucoes de deploy
- Next.js apenas se houver necessidade clara

## Regra Pratica
- V1 e a stack de entrega
- V2 e a stack de escala
- nada de V2 deve entrar antes de uma dor concreta e medida
