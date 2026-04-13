# Checklist - Camada API HTTP

- [ ] A rota chama Application service ou query apropriada
- [ ] Nao ha acesso direto a ORM sem justificativa arquitetural
- [ ] O tenant e resolvido na borda
- [ ] O ator autenticado e resolvido na borda
- [ ] O payload de erro segue contrato padrao
- [ ] `ErrorCodes` estao mapeados centralmente para HTTP
- [ ] Validacao de transporte esta separada da validacao de negocio
- [ ] Filtros, paginacao e ordenacao estao documentados quando aplicavel
- [ ] Rotas de reporting indicam dado parcial ou oficial
