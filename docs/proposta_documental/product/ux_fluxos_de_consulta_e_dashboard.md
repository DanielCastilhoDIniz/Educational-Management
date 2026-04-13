# UX - Fluxos de Consulta, Relatorios e Dashboard

## Objetivo
Documentar estados de tela e comportamento funcional de consultas, relatorios e painis analiticos.

## Estados Minimos
- carregando
- sem dados
- com dados parciais
- com dados oficiais
- sem permissao
- erro tecnico
- filtro invalido

## Fluxos Importantes

### Relatorio
1. usuario abre a tela
2. aplica filtros
3. visualiza resultado
4. refina ordenacao/paginacao
5. exporta, se permitido

### Boletim
1. usuario acessa boletim parcial ou oficial
2. sistema informa status do dado
3. usuario visualiza ou baixa documento permitido

### Painel do Estudante
1. usuario entra no painel
2. sistema carrega visao geral
3. usuario filtra por periodo, disciplina ou datas
4. sistema atualiza metricas mantendo contexto de oficial/parcial

## Regras de UX
- nao misturar dado parcial com rotulo de oficial
- filtros ativos devem ficar visiveis
- exportacao deve explicitar o mesmo recorte da tela
- mensagens de erro devem orientar o proximo passo do usuario
