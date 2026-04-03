# Organizacao Institucional e Hierarquia

## Objetivo
Descrever como o SaaS deve representar redes educacionais, instituicoes e unidades escolares.

## Niveis Conceituais

### 1. Rede Educacional
Representa o grupo, mantenedora ou organizacao superior que pode administrar mais de uma instituicao.

Exemplos:
- rede privada com varias escolas
- grupo educacional com campi em cidades diferentes
- organizacao mantenedora com varias unidades operacionais

### 2. Instituicao
Representa o tenant operacional primario.

A instituicao:
- possui usuarios, memberships, estudantes, professores e estrutura academica
- isola dados por padrao
- resolve a maior parte das politicas operacionais

### 3. Unidade Escolar
Representa escola, campus, polo ou unidade subordinada, quando necessario.

A unidade:
- pertence a uma instituicao
- pode ter calendario, turmas e operacao local conforme o produto evoluir
- nao substitui a instituicao como tenant principal sem decisao explicita

## Hierarquia Sugerida
`Network -> Institution -> Unit`

## Perguntas de Produto que Esta Hierarquia Resolve
- uma rede pode cadastrar mais de uma escola? sim
- uma instituicao pode ter mais de uma unidade? sim, se o modelo exigir
- um usuario pode atuar em mais de uma escola? sim, via membership e escopo
- relatorios podem consolidar mais de uma escola? sim, desde que isso seja contrato explicito e autorizado

## Regras Praticas
- se o produto ainda nao precisar de `Unit`, manter a documentacao preparada, mas a implementacao pode comecar em `Institution`
- nao confundir tenant com rede inteira sem decisao formal
- dashboards e relatorios devem explicitar em qual nivel estao agregando dados
