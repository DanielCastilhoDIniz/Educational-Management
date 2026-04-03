# Fitness Functions Arquiteturais

## Objetivo
Listar regras arquiteturais que idealmente devem ser verificadas continuamente por revisao ou automacao.

## Regras Sugeridas
- dominio nao importa Django ou framework de interface
- application nao acessa ORM diretamente
- interface HTTP nao chama aggregate nem repositorio concreto direto
- reporting nao usa aggregate transacional como fonte padrao para consultas pesadas
- erros expostos externamente passam por `ErrorCodes`
- tenant e ator sao considerados em operacoes relevantes
- eventos externos nao sao publicados antes do commit

## Uso
- checklist de review
- testes arquiteturais futuros
- linting estrutural quando viavel
