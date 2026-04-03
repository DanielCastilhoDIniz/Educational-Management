# Politica de Versionamento

## Objetivo
Definir como versionar artefatos do sistema que possuem contrato externo ou duradouro.

## Itens que Podem Exigir Versionamento
- API HTTP
- payloads de exportacao
- boletins oficiais
- contratos de eventos de integracao
- read models expostos externamente

## Regras Sugeridas
- mudanca breaking exige estrategia de versao ou transicao documentada
- boletins e documentos oficiais devem carregar versao de emissao quando aplicavel
- exportacoes devem indicar layout/versao quando o consumidor depender disso
- eventos de integracao devem ter esquema e compatibilidade pensados desde cedo

## Recomendacao
Nao versionar por reflexo. Versionar quando houver contrato externo real ou impacto operacional claro.
