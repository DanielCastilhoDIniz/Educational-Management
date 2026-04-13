# Freshness, Consistencia e Status do Dado

## Objetivo
Definir como relatorios, boletins e dashboards devem comunicar atualizacao, consistencia e oficialidade dos dados exibidos.

## Conceitos

### Dado Parcial
Dado sujeito a mudanca antes do fechamento ou consolidacao oficial.

### Dado Oficial
Dado consolidado segundo politicas e fechamento aplicaveis.

### Freshness
Janela esperada entre alteracao operacional e disponibilidade no modelo de leitura.

## Regras Sugeridas
- toda saida deve indicar se o dado e parcial ou oficial
- toda saida relevante deve expor `updated_at` ou `consolidated_at`
- painel do estudante pode trabalhar com dados parciais, desde que claramente identificados
- boletim oficial nao pode ser montado sobre dado parcial
- relatorios devem informar o recorte temporal e a data/hora de geracao

## Perguntas que a Documentacao Deve Fechar
- o refresh sera sincrono, near-real-time ou batch
- qual latencia e aceitavel por tipo de relatorio
- o que acontece quando parte do dado esta consolidada e parte nao
