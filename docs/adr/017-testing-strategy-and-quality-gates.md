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

## Checklist de Implementacao
- [x] Existem suites de testes por camada para dominio, application e infraestrutura
- [x] A CI ja executa testes e cobertura minima
- [ ] Gates de lint e tipagem estao integrados de forma obrigatoria na CI
- [ ] Estrategia de testes da camada HTTP esta documentada para a proxima fase
- [ ] Ha estrategia explicita para factories, dados de teste e testes de migracao

## Checklist de Code Review
- [x] Regras de negocio centrais continuam sendo testadas primeiro no dominio
- [ ] Testes de application nao dependem desnecessariamente de ORM
- [ ] Testes de infraestrutura focam adapters reais e nao reexecutam regra do dominio
- [ ] Gates de qualidade sao aplicados de forma consistente em PR e main

## Checklist de Testes
- [x] Dominio cobre invariantes e transicoes
- [x] Application cobre orquestracao, erros e integridade de eventos
- [x] Infraestrutura cobre repositorio, concorrencia e reidratacao
- [ ] Interface/API tera testes de contrato quando a camada HTTP surgir

## Checklist de Documentacao
- [ ] Matriz de rastreabilidade documento x teste esta atualizada
- [ ] Guia de contribuicao referencia os gates de qualidade oficiais
- [ ] Cobertura minima e regras de excecao estao documentadas

