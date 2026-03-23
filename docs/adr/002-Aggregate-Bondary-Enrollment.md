# ADR 002 - Fronteira do Aggregate Matricula e Regras Dependentes de Contexto Externo

## Status
Aprovado

## Contexto
Algumas regras do negocio dependem de dados e estados que nao pertencem ao aggregate Matricula, por exemplo:

- turma ativa/inativa
- periodo letivo ativo/encerrado
- calendario
- politicas institucionais
- resultados pedagogicos

Se essas dependencias forem colocadas dentro do aggregate, o dominio perde pureza, testabilidade e cria acoplamento forte com a infraestrutura.

## Decisao
Definir a fronteira rigida:

### O aggregate Matricula valida apenas invariantes internas
- estado da matricula
- coerencia de timestamps por estado
- transicoes permitidas
- exigencia de justificativa quando a transicao do dominio exigir
- emissao interna de eventos do proprio aggregate

### Regras dependentes de contexto externo ficam fora do aggregate
Devem ser validadas na:

- Application Layer
- contextos especializados (Turmas, Periodos, Frequencia, Avaliacao, Monitoramento)

## Consequencias

### Positivas
- dominio da matricula permanece puro e altamente testavel
- contextos podem evoluir independentemente
- reduz refatoracoes quando calendario/politicas mudam
- clarifica responsabilidades por camada

### Negativas / Riscos
- services de application ficam responsaveis por pre-condicoes externas
- exige disciplina para nao vazar regras externas para o aggregate
- necessita documentacao explicita

## Regras e Invariantes
- o aggregate Matricula nao consulta Turma/Periodo/Calendario/Politicas diretamente
- pre-condicoes externas devem estar documentadas no caso de uso
- qualquer validacao externa deve ocorrer antes de executar a transicao do aggregate
- a infra nao toma decisao de negocio

## Plano de Implementacao
- revisar capitulos 6-9 para explicitar fronteiras
- revisar capitulo 5 para separar transicoes internas de pre-condicoes externas
- nos services de application, validar pre-condicoes externas antes de chamar o dominio

## Checklist de Implementacao
- [x] Atualizar Cap. 5 para separar:
  - [x] transicoes internas do aggregate
  - [x] pre-condicoes externas (turma/periodo/calendario/politicas)
- [x] Atualizar Caps. 6-9 com secao "Escopo e fronteira"
- [ ] Criar/atualizar `docs/use_cases` com pre-condicoes explicitas
- [x] Padronizar onde politicas sao lidas (Cap. 11 + Tabela de Implementacao)

## Checklist de Code Review
- [x] Aggregate Matricula nao faz IO nem consulta servicos externos
- [x] Nao ha import do dominio de Turma/Periodo dentro do dominio de Matricula
- [ ] Application valida pre-condicoes externas antes de transicoes
- [ ] Erros de pre-condicao sao diferentes de erros de dominio

## Checklist de Testes
- [x] Testes de dominio cobrem invariantes internas (sem dependencias externas)
- [ ] Testes de application cobrem pre-condicoes externas (com doubles/stubs)
- [ ] Casos de uso documentados refletem o comportamento testado
