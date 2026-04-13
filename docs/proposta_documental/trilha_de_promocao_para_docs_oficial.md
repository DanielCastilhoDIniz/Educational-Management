# Trilha de Promocao para a Documentacao Oficial

## Objetivo
Definir em que ordem os documentos do pacote proposto devem migrar para a trilha oficial de `docs/`, priorizando o que reduz risco imediato e o que habilita o crescimento do SaaS sem retrabalho.

## Principios da Promocao
- documento sobe primeiro quando reduz ambiguidade real do projeto atual
- documento sobe quando ja existe decisao minimamente madura para sustenta-lo
- documento muito especulativo permanece em `docs/proposta_documental/` ate ganhar patrocinio e dono
- primeiro sobem contratos e fronteiras; depois detalhes operacionais; por ultimo documentos de expansao ou otimizacao

## Destinos Oficiais Sugeridos
- ADRs aprovados continuam em `docs/adr/`
- casos de uso aprovados vao para `docs/use_cases/`
- politicas aprovadas devem ganhar um diretorio oficial proprio, sugerido: `docs/policies/`
- visao de produto e contextos podem ir para `docs/product/` ou `docs/contexts/`, se esses diretorios forem adotados
- docs de relatorios e analytics podem virar `docs/reporting/`
- docs especificos da API podem virar `docs/interfaces/` ou `docs/api/`
- checklists aprovados podem virar `docs/checklists/` e tambem ser referenciados em PR templates e README

## Onda 1 - Fundacao de Plataforma
Promover primeiro porque essas decisoes contaminam todos os contextos futuros.

### Promover
- `visao_produto_saas.md`
- `contexts/mapa_de_bounded_contexts.md`
- `adr/019-multi-tenant-and-institution-isolation.md`
- `adr/020-identity-access-and-membership.md`
- `policies/politica_multi_tenancy_e_isolamento.md`
- `policies/politica_identidade_papeis_e_permissoes.md`
- `checklists/08-multi_tenancy_e_autorizacao.md`

### Motivo
Sem isso, o produto corre o risco de crescer com tenant implito, roles difusas e autorizacao ad hoc.

### Resultado Esperado
- contexto institucional deixa de ser suposicao
- usuarios e memberships passam a ter fronteira conceitual clara
- novos modulos nascem tenant-aware por padrao

## Onda 2 - Modulo de Matricula e Contratos Ja Vivos
Promover logo depois porque esse e o contexto mais maduro do codigo atual.

### Promover
- `adr/012-create-enrollment-contract.md`
- `adr/013-error-taxonomy-and-failure-mapping.md`
- `adr/014-enrollment-state-matrix-and-lifecycle-timestamps.md`
- `use_cases/criar_matricula.md`
- `use_cases/consultar_matricula_por_id.md`
- `use_cases/suspender_matricula.md`
- `use_cases/reativar_matricula.md`
- `use_cases/cancelar_matricula.md`
- `use_cases/concluir_matricula.md`
- `policies/politica_criacao_de_matricula.md`
- `policies/politica_conclusao_elegibilidade.md`
- `policies/politica_cancelamento_e_justificativa.md`
- `policies/politica_suspensao_e_reativacao.md`
- `policies/politica_timestamps_e_utc.md`

### Motivo
Esses documentos fecham lacunas diretamente ligadas ao desenho e aos testes que ja existem ou estao muito proximos do codigo atual.

### Resultado Esperado
- criacao de matricula deixa de ser ponto cego
- matriz de erros e estados fica oficializada
- use cases de matricula ficam padronizados

## Onda 3 - Fundacao Academica e Cadastro Mestre
Promover quando o produto entrar claramente na fase de cadastro institucional amplo.

### Promover
- `adr/021-academic-structure-school-year-period-class-group-subject.md`
- `adr/024-student-guardian-and-contact-data.md`
- `use_cases/cadastrar_usuario.md`
- `use_cases/vincular_usuario_a_instituicao_e_papel.md`
- `use_cases/cadastrar_estudante.md`
- `use_cases/cadastrar_responsavel_e_vincular_ao_estudante.md`
- `use_cases/cadastrar_professor.md`
- `use_cases/criar_ano_letivo_e_periodos.md`
- `use_cases/criar_turma.md`
- `use_cases/associar_professor_a_disciplina_e_turma.md`
- `policies/politica_ano_letivo_periodos_e_turmas.md`
- `policies/politica_estudante_responsavel_e_contatos.md`
- `policies/politica_vinculo_professor_disciplina_turma.md`

### Motivo
Esses documentos estabilizam os dados mestres do dominio escolar e evitam que matricula, diario e avaliacao crescam sobre bases fragis.

### Resultado Esperado
- dados mestres e chaves de negocio ficam claros
- papeis de secretaria, professor e responsavel passam a ter lugar arquitetural
- ano letivo, periodo e turma deixam de ser estruturas improvisadas

## Onda 4 - Operacao Escolar Recorrente
Promover quando o time entrar de fato em diario, frequencia e notas.

### Promover
- `adr/022-attendance-and-lesson-journal.md`
- `adr/023-assessment-gradebook-and-period-closing.md`
- `use_cases/registrar_aula.md`
- `use_cases/lancar_frequencia.md`
- `use_cases/lancar_avaliacao_e_notas.md`
- `use_cases/fechar_periodo_e_calcular_media.md`
- `policies/politica_frequencia_e_reposicao.md`
- `policies/politica_regime_avaliativo_e_formula_de_media.md`
- `checklists/10-diario_frequencia_e_avaliacao.md`
- `checklists/11-fechamento_de_periodo.md`

### Motivo
Esse bloco representa a operacao escolar cotidiana e precisa subir como conjunto coerente, nao como documentos isolados.

### Resultado Esperado
- diario, frequencia e avaliacao passam a compartilhar uma linguagem comum
- fechamento de periodo deixa de ser detalhe tardio
- insumos de reporting ficam mais confiaveis

## Onda 5 - Reporting, Boletins e Painel do Estudante
Promover quando o produto precisar transformar dados operacionais em consulta gerencial, saida formal e experiencia do estudante.

### Promover
- `adr/025-reporting-and-official-records.md`
- `adr/026-reporting-read-models-and-query-contracts.md`
- `adr/027-report-filters-exports-and-pagination.md`
- `adr/028-student-dashboard-and-metric-aggregation.md`
- `reporting/catalogo_de_relatorios_e_saidas.md`
- `reporting/matriz_de_filtros_relatorios.md`
- `reporting/dicionario_de_metricas_academicas.md`
- `reporting/especificacao_painel_do_estudante.md`
- `use_cases/emitir_relatorio_de_frequencia.md`
- `use_cases/emitir_relatorio_de_aulas_registradas.md`
- `use_cases/emitir_relatorio_de_desempenho_por_disciplina.md`
- `use_cases/emitir_boletim_oficial.md`
- `use_cases/consultar_boletim_do_estudante.md`
- `use_cases/consultar_painel_do_estudante.md`
- `policies/politica_relatorios_e_filtros.md`
- `policies/politica_emissao_de_boletim_e_versao_oficial.md`
- `policies/politica_painel_do_estudante_e_visibilidade.md`
- `checklists/12-relatorios_consultas_e_exportacoes.md`
- `checklists/13-boletim_dashboard_e_metricas.md`

### Motivo
Esse grupo impede que relatorios e dashboards nascam como consultas oportunistas sem contrato, sem filtro consistente e sem regra clara de oficialidade.

### Resultado Esperado
- relatorios passam a ter catalogo e filtros padrao
- exportacao fica coerente com a tela
- boletim ganha trilha de versao oficial
- painel do estudante nasce sustentado por metricas definidas

## Onda 6 - Camada API HTTP
Promover quando o time decidir expor os primeiros casos de uso por HTTP ou outra interface remota equivalente.

### Promover
- `adr/029-api-delivery-strategy-and-http-surface.md`
- `interfaces/guia_da_camada_api_http.md`
- `interfaces/api_autenticacao_membership_e_contexto_de_tenant.md`
- `interfaces/api_rotas_http_fase_1_enrollment.md`
- `interfaces/api_rotas_http_fase_2_queries_reporting_e_dashboard.md`
- `interfaces/api_payloads_de_erro_e_metadados.md`
- `interfaces/api_presenters_serializacao_e_versionamento.md`
- `interfaces/catalogo_de_comandos_e_queries.md`
- `interfaces/mapeamento_http_e_codigos_de_erro.md`
- `checklists/14-camada_api_http.md`

### Motivo
Esse grupo evita que a API nasca como detalhe acoplado ao framework, sem tenancy, sem contrato de erro e sem separacao clara entre command side e query side.

### Resultado Esperado
- a borda HTTP nasce fina e previsivel
- a API respeita `ApplicationResult` e `ErrorCodes`
- enrollment vira a primeira superficie publica de forma segura
- reporting e dashboard entram na API sem comprometer a arquitetura

## Onda 7 - Operacao, Eventos, Qualidade e Escala
Promover por ultimo, mas antes da fase de escala real do produto.

### Promover
- `adr/015-actor-authority-and-audit-responsibility.md`
- `adr/016-domain-event-delivery-and-outbox.md`
- `adr/017-testing-strategy-and-quality-gates.md`
- `adr/018-observability-audit-and-operational-support.md`
- `policies/politica_privacidade_e_lgpd.md`
- `checklists/01-prontidao_arquitetural.md`
- `checklists/02-definicao_de_caso_de_uso.md`
- `checklists/03-persistencia_e_migracoes.md`
- `checklists/04-testes_e_ci.md`
- `checklists/05-revisao_de_pr.md`
- `checklists/06-release_readiness.md`
- `checklists/07-novo_contexto_de_negocio.md`
- `checklists/09-seguranca_privacidade_e_auditoria.md`

### Motivo
Esse grupo sustenta escala, compliance, suporte e release seguro. Ele e estrategico, mas rende mais quando o produto ja tem contornos funcionais mais firmes.

### Resultado Esperado
- produto fica pronto para integracoes externas, auditoria e suporte mais serio
- checklists deixam de ser opcionais e passam a orientar execucao real
- documentos oficiais passam a refletir nao so o desenho, mas tambem a operacao

## O que Eu Promoveria Ja
Se fosse escolher os primeiros documentos para subir agora, eu promoveria nesta ordem:

1. `visao_produto_saas.md`
2. `contexts/mapa_de_bounded_contexts.md`
3. `adr/019-multi-tenant-and-institution-isolation.md`
4. `adr/020-identity-access-and-membership.md`
5. `adr/012-create-enrollment-contract.md`
6. `adr/013-error-taxonomy-and-failure-mapping.md`
7. `adr/014-enrollment-state-matrix-and-lifecycle-timestamps.md`
8. `use_cases/criar_matricula.md`
9. `policies/politica_criacao_de_matricula.md`
10. `policies/politica_timestamps_e_utc.md`

## Criterio de Encerramento por Onda
Uma onda so deve ser considerada promovida quando:
- os documentos foram revisados pelo time
- houve decisao explicita de aprovacao ou rejeicao
- o destino oficial foi definido
- o README oficial ou mapa documental passou a apontar para eles
- os checklists relevantes foram acoplados ao fluxo real de desenvolvimento, quando aplicavel
