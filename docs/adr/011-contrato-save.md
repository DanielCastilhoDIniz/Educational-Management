# o contrato do save

### Responsabilidade do método

Persistir atualização de matrícula existente com concorrência otimista.

### Entrada

Aggregate existente com versão de origem.

### Saída

Nova versão persistida.

### Casos de sucesso

Registro existe e versão bate.
- registro existe
- a versão bate
- atualiza os campos
- incrementa a versão/retorna a nova versão

### Casos de falha

1. registro ausente para atualização

Nome conceitual: `EnrollmentPersistenceNotFoundError`

ou equivalente

2. conflito de concorrência

Nome conceitual:`ConcurrencyConflictError`

3. erro de integridade de dados

Nome conceitual:`DataIntegrityError`


4. falha técnica inesperada

Nome conceitual: `PersistenceError`

ou similar como fallback

### Regras técnicas

incremento automático de versão

sem sobrescrita

sem mescla

sem create implícito


Quando a gravação for aceita, o repository deve persistir corretamente:

state

concluded_at

cancelled_at

suspended_at

version nova

e preservar:

id

student_id

class_group_id

academic_period_id

created_at