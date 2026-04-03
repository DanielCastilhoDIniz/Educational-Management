# Politica - Suspensao e Reativacao

## Objetivo
Definir regras externas que permitam ou bloqueiem suspensao e reativacao.

## Regras Sugeridas
- suspensao exige justificativa e estado atual `active`
- reativacao exige justificativa e estado atual `suspended`
- politicas podem impor prazo maximo de suspensao
- reativacao pode depender de regularizacao externa
- toda excecao deve ser auditavel

## Perguntas para Fechar
- ha limite de numero de suspensoes por periodo
- ha prazo maximo entre suspensao e reativacao
- ha bloqueios externos que impedem reativacao

## Testes Recomendados
- suspensao permitida
- suspensao proibida por politica externa
- reativacao permitida
- reativacao bloqueada por pendencia externa
