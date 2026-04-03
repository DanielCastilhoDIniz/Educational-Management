# Mapa de Dependencias entre Contextos

## Objetivo
Definir direcao desejada de dependencias entre contextos para evitar acoplamento indevido.

## Direcoes Permitidas
- interface depende de application
- application depende de ports e dominio
- infraestrutura implementa ports
- reporting consome read models e contratos de consulta
- auth/membership e transversal, mas nao deve puxar regra nuclear de outros contextos

## Alertas de Acoplamento
- diario conhecendo internals de matricula alem do contrato necessario
- interface consultando ORM de varios contextos sem passar por query layer
- politicas institucionais espalhadas em varios modulos sem catalogo central

## Regra Pratica
Dependencia estrutural entre contextos deve ser rara, explicita e documentada.
