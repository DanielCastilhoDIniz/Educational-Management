# ADR 017 - Estrategia de Testes e Gates de Qualidade

## Status
Proposto

## Contexto
O modulo ja possui boa cobertura de dominio, application e repositorio, mas ainda se beneficia de uma politica documental clara para sustentar crescimento sem regressao.

## Decisao
Adotar uma estrategia de testes por camada com gates minimos de qualidade em CI.

## Piramide Proposta

### Dominio
- testes de invariantes
- testes de transicoes validas e invalidas
- testes de round-trip sem ORM

### Application
- testes de orquestracao
- testes de traducao de erros
- testes de integridade do fluxo evento/persistencia

### Infraestrutura
- testes de integracao do repositorio
- testes de migracao quando houver evolucao de schema
- testes de contrato do mapper

### Interface
- testes de mapeamento HTTP quando a API existir
- testes de serializacao de `ApplicationResult`

## Gates Minimos
- suite `pytest` verde
- cobertura minima documentada e revisada periodicamente
- falha de lint/tipo bloqueia merge quando adotado oficialmente
- migracao sem teste de rollback/compatibilidade nao deve entrar sem excecao documentada

## Consequencias
- reduz regressao silenciosa
- melhora onboarding e review
- exige disciplina para nao tratar cobertura isolada como qualidade suficiente

## Plano de Implementacao
- consolidar suites por camada
- definir comandos oficiais de CI
- adotar checklist de PR e release
- incluir testes obrigatorios para todo novo caso de uso
