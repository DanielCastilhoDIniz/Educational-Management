# Politica - Hierarquia Organizacional e Cadastro de Rede

## Objetivo
Definir como redes educacionais, instituicoes e unidades podem ser cadastradas e relacionadas.

## Regras Sugeridas
- uma rede pode possuir uma ou mais instituicoes
- uma instituicao pode possuir zero ou mais unidades escolares
- a unicidade de nome/identificador deve ser definida por escopo apropriado
- consolidacao cross-school so e permitida para atores autorizados
- criacao de unidade nao pode romper o isolamento por instituicao

## Perguntas para Fechar
- `Network` sera obrigatoria ou opcional no produto
- uma escola isolada sera modelada apenas como `Institution`
- `Unit` existira desde a v1 ou apenas em clientes que precisarem

## Testes Recomendados
- cadastro de mais de uma instituicao na mesma rede
- cadastro de mais de uma unidade na mesma instituicao
- negacao de acesso cross-school sem permissao
- relatorio consolidado apenas para ator autorizado
