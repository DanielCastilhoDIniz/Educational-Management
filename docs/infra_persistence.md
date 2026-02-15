
Para garantir a integridade entre o sistema e a persistência, adotaremos uma estratégia de mapeamento direto por espelhamento, onde a estrutura do banco de dados reflete fielmente o estado do Agregado de Domínio. Nesta abordagem, a tabela principal de matrículas atuará como um snapshot em tempo real, contendo colunas que correspondem exatamente aos atributos da entidade, como a coluna state (representando o EnrollmentState). Simultaneamente, a lista interna de transitions será persistida em uma tabela de histórico relacionada via chave estrangeira, garantindo que cada mudança de estado registrada no objeto de domínio possua um lastro físico idêntico no banco de dados. Esse alinhamento elimina ambiguidades na tradução de dados e facilita a reidratação da entidade, permitindo que o repositório reconstrua o objeto com sua história completa sem a necessidade de lógicas de conversão complexas.



Tabela Enrollment (estado atual)

Campos mínimos?

id (o mesmo id do domínio)
student_id,
class_group_id,
academic_period_id
state (enum/string)
created_at
concluded_at, cancelled_at, suspended_at (nullable)


2.2. Tabela EnrollmentTransition (histórico / auditoria)

Uma linha por transição relevante:
enrollment_id (FK)
occurred_at
action (CONCLUDE/CANCEL/SUSPEND)
from_state, to_state
justification (nullable, mas gravada quando existir)
Justificativa: seu domínio já trata transição como “fato”, então persistir isso é auditoria natural e baratíssima.

. Tabela Enrollment (Snapshot do Agregado)
[ ] Primary Key: O id deve permitir valores gerados pela aplicação (ex: UUID ou string), já que o domínio define esse ID antes de salvar.

[ ] Indexação de Busca: Índices criados para student_id e state. Sem isso, relatórios de "Alunos Ativos" ficarão lentos no futuro.

[ ] Timestamps de Auditoria Técnica: Inclusão de created_at e updated_at.

[ ] Campos de Negócio (Nullable): concluded_at, cancelled_at e suspended_at definidos como opcionais (NULL), pois só são preenchidos no fim do ciclo de vida.

[ ] Constraint de Estado: (Opcional) Uma CHECK constraint para garantir que a string no banco pertença aos valores permitidos pelo seu Enum de domínio.

2. Tabela EnrollmentTransition (Log de Fatos)
[ ] Identificação Única: Cada linha de transição tem seu próprio id (independente do enrollment_id).

[ ] Rastreabilidade de Autor: Campo actor_id presente (quem executou a ação).

[ ] Imutabilidade: Configurada para ser append-only (nunca deletar ou editar linhas nesta tabela).

[ ] Deduplicação (Unique Key): Constraint única composta para evitar repetição acidental: (enrollment_id, occurred_at, action).

[ ] Tipos de Dados:

justification: Tipo TEXT (para suportar textos longos).

occurred_at: Tipo TIMESTAMP WITH TIME ZONE.

Regras de Integridade e Transação
[ ] Atomicidade: O Repositório deve abrir uma BEGIN TRANSACTION antes de atualizar a Enrollment e inserir na EnrollmentTransition. Se uma falhar, as duas devem falhar.

[ ] Foreign Key: enrollment_id apontando para a tabela principal com ON DELETE PROTECT. (Nunca apague o rastro se a matrícula sumir).

[ ] Ordenação Nativa: Índice no campo occurred_at para que a reidratação (o from_orm) traga o histórico ordenado sem esforço do banco.


from_orm → Domínio (Reidratação)
Quando você busca um dado, você não está apenas criando um objeto, você está reidratando uma entidade com sua história.

O Desafio: O banco de dados retorna uma linha da tabela enrollments e várias linhas da tabela enrollment_transitions.

A Conversão:

Mapeia colunas básicas: model.id → entity.id.

Atenção aos Enums: Converte a string do banco de volta para o Enum EnrollmentState(model.state).

A História: Transforma cada TransitionModel em um StateTransition (Value Object) e coloca na lista entity.transitions.

O Resultado: Uma instância de Enrollment pronta para executar métodos como .conclude().

3.2. from_domain → ORM (Persistência)
Aqui o processo é inverso. O Domínio é a fonte da verdade.

O Desafio: A entidade pode ter novas transições na lista que ainda não existem no banco.

A Conversão:

Sincronização de Estado: O model.state recebe o entity.state.value.

Snapshot de Datas: Atualiza concluded_at, cancelled_at, etc.

Novas Transições: Você compara as transições da entidade com as que já estão no banco (ou apenas insere as novas).

O Resultado: O ORM  gera os comandos UPDATE e INSERT necessários.