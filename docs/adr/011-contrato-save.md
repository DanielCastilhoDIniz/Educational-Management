# Contrato do método `save`

## Responsabilidade
Persistir a atualização de uma matrícula existente usando concorrência otimista.

## Entrada
- Um aggregate `Enrollment` existente, semanticamente válido, contendo a versão de origem esperada para a atualização.

## Pré-condições
- O aggregate representa uma matrícula já existente
- A `version` do aggregate é a versão de origem usada como condição de concorrência
- O método não realiza criação implícita

## Saída
- A nova versão persistida da matrícula

## Condição de sucesso
A atualização só pode ser concluída quando:
- O registro com o `id` informado existe no banco
- A `version` persistida atual é igual à `version` de origem do aggregate

## Efeitos em caso de sucesso
- Persiste o novo snapshot da matrícula
- Incrementa a versão automaticamente em 1
- Retorna a nova versão persistida

### Campos atualizados
Quando a gravação for aceita, o repository deve persistir corretamente:
- `state`
- `concluded_at`
- `cancelled_at`
- `suspended_at`
- `version` nova

### Campos preservados
O repository deve manter corretamente os dados estruturais já existentes da matrícula, incluindo:
- `id`
- `student_id`
- `class_group_id`
- `academic_period_id`
- `created_at`

## Casos de falha

1. **Registro ausente para atualização**
   - O `id` informado não existe no momento do `save`
   - Nome conceitual sugerido: `EnrollmentPersistenceNotFoundError`

2. **Conflito de concorrência**
   - O registro existe, mas a `version` persistida atual não coincide com a `version` de origem do aggregate
   - Nome conceitual sugerido: `ConcurrencyConflictError`

3. **Erro de integridade de dados**
   - A persistência falha por violação de constraint, referência ou outra inconsistência estrutural de dados
   - Nome conceitual sugerido: `DataIntegrityError`

4. **Falha técnica inesperada**
   - A persistência falha por motivo técnico não classificado nas categorias anteriores
   - Nome conceitual sugerido: `PersistenceError`

## Regras técnicas
- Incremento automático de versão
- Sem sobrescrita
- Sem mescla
- Sem create implícito

### Estratégia de diagnóstico quando nenhuma atualização ocorrer
Se a tentativa de atualização condicional não afetar nenhum registro:
1. Verificar se o `id` existe
2. Se não existir, lançar erro de registro ausente para atualização (`EnrollmentPersistenceNotFoundError`)
3. Se existir, lançar erro de conflito de concorrência (`ConcurrencyConflictError`)

## Não responsabilidades
- Não criar matrícula nova
- Não aplicar regras de negócio do domínio
- Não publicar eventos externos
- Não limpar domain events
- Não resolver conflitos por merge