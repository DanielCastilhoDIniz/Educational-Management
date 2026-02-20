# ADR 004 — Fronteira do Aggregate Matrícula e Regras Dependentes de Contexto Externo
# ADR 004 — Aggregate Boundary, Enrollment, and Rules Dependent on External Context

## Status
Aprovado

## Contexto
Algumas regras do negócio dependem de dados e estados que não pertencem ao aggregate Matrícula,
por exemplo:
- Turma ativa/inativa
- Período letivo ativo/encerrado
- Calendário (janelas de prazo)
- Políticas institucionais (mínimo de dias, percentuais, exceções)
- Resultados pedagógicos (veredito, conselho)

Se essas dependências forem colocadas dentro do aggregate Matrícula, o domínio:
- passa a depender de outros contextos,
- perde pureza e testabilidade,
- e cria acoplamento forte com a infraestrutura.

## Decisão
Definir a fronteira rígida:

### O Aggregate Matrícula valida apenas invariantes internas
- estado da matrícula
- coerência de timestamps por estado
- transições permitidas
- exigência de justificativa quando a transição do domínio exigir
- emissão interna de eventos do próprio aggregate

### Regras dependentes de contexto externo ficam fora do aggregate
Devem ser validadas na:
- Application Layer (pré-condições do caso de uso), e/ou
- Contextos especializados (Turmas, Períodos, Frequência, Avaliação, Monitoramento)

## Consequências

### Positivas
- Domínio da Matrícula permanece puro e altamente testável.
- Contextos podem evoluir independentemente.
- Reduz refatorações quando regras de calendário/políticas mudam.
- Clarifica responsabilidades por camada.

### Negativas / Riscos
- Application Services ficam responsáveis por orquestrar pré-condições externas.
- Exige disciplina: não “vazar” regras externas para o aggregate por conveniência.
- Necessita documentação explícita (o que é invariante interna vs pré-condição externa).

## Regras e Invariantes
- Aggregate Matrícula não consulta Turma/Período/Calendário/Políticas diretamente.
- Pré-condições externas devem estar documentadas no caso de uso (docs/use_cases).
- Qualquer validação externa deve ocorrer antes de executar a transição do aggregate.
- A infra não toma decisão de negócio (apenas persiste/publica).

## Plano de Implementação
- Revisar capítulos 6–9 (Frequência, Avaliações, Resultado, Evasão) para explicitar fronteiras.
- Revisar Cap. 5 (Transições) para:
  - manter transições como contrato do aggregate,
  - mover calendário/prazo/políticas para pré-condições/políticas configuráveis.
- Nos Application Services:
  - validar pré-condições externas antes de chamar o domínio.

## Checklist de Implementação
- [ ] Atualizar Cap. 5 para separar:
  - [ ] transições internas do aggregate
  - [ ] pré-condições externas (turma/período/calendário/políticas)
- [ ] Atualizar Caps. 6–9 com seção “Escopo e fronteira”
- [ ] Criar/atualizar docs/use_cases com pré-condições explícitas
- [ ] Padronizar onde políticas são lidas (Cap. 11 + Tabela de Implementação)

## Checklist de Code Review
- [ ] Aggregate Matrícula não faz IO nem consulta serviços externos
- [ ] Não há import do domínio de Turma/Período dentro do domínio de Matrícula
- [ ] Application valida pré-condições externas antes de transições
- [ ] Erros de pré-condição são diferentes de erros de domínio (contrato claro)

## Checklist de Testes
- [ ] Testes de domínio cobrem invariantes internas (sem dependências externas)
- [ ] Testes de application cobrem pré-condições externas (com doubles/stubs)
- [ ] Casos de uso documentados refletem o comportamento testado