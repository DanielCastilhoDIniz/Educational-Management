# Recomendacoes por Camada

## Backend
Recomendacao:
- Django + DRF + django-filter

Motivo:
- ja conversa com a base atual
- forte ecossistema para auth, admin, ORM, migrations e API

## Dominio e Application
Recomendacao:
- manter puro em Python, sem acoplamento a framework

Motivo:
- preserva testabilidade e aderencia aos ADRs atuais

## Banco
Recomendacao:
- PostgreSQL

Motivo:
- excelente para integridade, consultas relacionais e auditabilidade

## Cache/Fila
Recomendacao:
- Redis

Motivo:
- simples, maduro e suficiente para fase inicial

## Jobs
Recomendacao:
- Celery

Motivo:
- bom encaixe com Django e casos de uso assincronos do produto

## Frontend
Recomendacao:
- React + TypeScript + Vite + TanStack Query + Tailwind

Motivo:
- produtividade alta, ecossistema forte e baixa friccao para um backend API-first

## Testes
Recomendacao:
- pytest no back, Vitest e Playwright no front

Motivo:
- equilibrio bom entre velocidade e cobertura funcional

## Deploy
Recomendacao:
- Docker + GitHub Actions + servicos gerenciados

Motivo:
- simplicidade operacional com caminho claro para crescer
