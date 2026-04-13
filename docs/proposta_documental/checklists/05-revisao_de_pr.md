# Checklist - Revisao de PR

- [ ] A mudanca respeita os ADRs vigentes ou propoe um novo ADR
- [ ] Nao move regra externa para dentro do aggregate
- [ ] Nao vaza detalhe tecnico como contrato externo sem necessidade
- [ ] Nao quebra o fluxo persistencia -> eventos
- [ ] Erros esperados continuam com codigo estavel
- [ ] Logs e auditoria continuam suficientes
- [ ] Nomes e termos seguem a linguagem ubiqua
- [ ] Os testes refletem o contrato real e nao um cenario artificial confuso
