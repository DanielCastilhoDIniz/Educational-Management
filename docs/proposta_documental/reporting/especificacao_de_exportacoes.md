# Especificacao de Exportacoes

## Objetivo
Definir padroes para exportacao CSV, XLSX e PDF de relatorios, boletins e consultas permitidas.

## Regras Sugeridas
- exportacao deve refletir os mesmos filtros da tela de origem
- arquivo deve registrar filtros usados, data/hora de geracao e ator emissor quando aplicavel
- timezone exibido deve ser padronizado e documentado
- limites de volume devem ser definidos por tipo de exportacao
- exportacoes sensiveis devem ser auditadas

## Tipos de Exportacao

### CSV
- foco em interoperabilidade e volume

### XLSX
- foco em analise administrativa e coordenacao

### PDF
- foco em emissao formal, boletim e compartilhamento controlado

## Metadados Minimos
- nome do relatorio
- tenant
- filtros
- data/hora de geracao
- tipo do dado (`partial` ou `official`)
