# Runbooks Operacionais

## Objetivo
Registrar procedimentos operacionais para suporte, diagnostico e tratamento de incidentes comuns do SaaS escolar.

## Runbooks Iniciais Sugeridos

### Boletim emitido com dado desatualizado
- confirmar periodo e status do dado
- confirmar refresh do read model
- confirmar versao do boletim emitido
- avaliar necessidade de reemissao

### Relatorio de frequencia inconsistente
- validar filtros usados
- validar se houve retificacao de frequencia
- validar freshness do read model
- registrar incidente se houver divergencia entre operacional e reporting

### Painel do estudante mostrando metricas divergentes
- validar status parcial vs oficial
- validar periodo selecionado
- validar dados de origem do dashboard

### Exportacao incompleta ou truncada
- validar limite operacional
- validar filtros e paginacao
- avaliar necessidade de job assincromo

### Fechamento de periodo com pendencias
- listar pendencias de diario, frequencia e nota
- verificar politica de excecao
- registrar ator e decisao operacional
