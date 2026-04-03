# Caso de Uso - Cadastrar Rede, Instituicao e Unidade

## Objetivo
Permitir a configuracao da estrutura organizacional do produto para suportar mais de uma escola e, quando necessario, uma rede educacional com multiplas unidades.

## Atores
- administrador da plataforma
- administrador de rede, quando esse papel existir

## Entrada Conceitual
- dados da rede educacional, quando aplicavel
- dados da instituicao
- dados da unidade escolar, quando aplicavel
- `actor_id`

## Pre-condicoes
- ator autorizado
- nomes e identificadores organizacionais validos
- nao haver duplicidade segundo a politica de cadastro organizacional

## Fluxo Principal
1. Validar autorizacao.
2. Criar ou localizar a rede educacional, quando aplicavel.
3. Criar a instituicao associada.
4. Criar a unidade escolar, quando aplicavel.
5. Registrar auditoria.
6. Retornar a estrutura organizacional criada.

## Fluxos Alternativos
- duplicidade de rede ou instituicao
- ator sem permissao
- configuracao hierarquica invalida

## Pos-condicoes
- a organizacao fica preparada para receber usuarios, memberships e operacao academica
- a hierarquia `rede -> instituicao -> unidade` fica rastreavel quando usada
