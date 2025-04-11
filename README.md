# Sistema de Gestão - Guia de Migrações do Banco de Dados

## Visão Geral
Este projeto utiliza Flask-Migrate (baseado no Alembic) para gerenciar as migrações do banco de dados. Isso permite que você faça alterações no banco de dados de forma segura e controlada, mantendo a consistência dos dados durante os deploys.

## Comandos Essenciais

### Criar uma Nova Migração
Quando você fizer alterações nos modelos (models.py), crie uma nova migração:
```bash
flask db migrate -m "descrição da alteração"
```

### Aplicar Migrações Pendentes
Para aplicar todas as migrações pendentes:
```bash
flask db upgrade
```

### Reverter Migrações
Se necessário, você pode reverter a última migração:
```bash
flask db downgrade
```

## Processo de Deploy

1. **Antes do Deploy**
   - Faça backup do banco de dados
   - Teste as migrações em um ambiente de desenvolvimento

2. **Durante o Deploy**
   - Execute `flask db upgrade` para aplicar as migrações pendentes
   - Verifique os logs para garantir que as migrações foram aplicadas com sucesso

3. **Após o Deploy**
   - Verifique se a aplicação está funcionando corretamente
   - Monitore os logs para identificar possíveis problemas

## Boas Práticas

1. **Sempre Versione as Migrações**
   - Mantenha todas as migrações no controle de versão
   - Nunca modifique migrações já aplicadas em produção

2. **Teste as Migrações**
   - Teste cada migração em um ambiente de desenvolvimento
   - Verifique se os dados existentes não serão afetados negativamente

3. **Backup**
   - Sempre faça backup do banco de dados antes de aplicar migrações em produção
   - Mantenha um plano de rollback para cada migração

4. **Documentação**
   - Documente alterações significativas nas migrações
   - Mantenha um registro das migrações aplicadas em cada ambiente

## Solução de Problemas

### Erro ao Criar Migração
Se encontrar erros ao criar uma migração:
1. Verifique se todos os modelos estão corretamente definidos
2. Certifique-se de que as importações estão corretas
3. Execute `flask db stamp head` se o banco de dados e as migrações estiverem dessincronizados

### Erro ao Aplicar Migração
Se encontrar erros ao aplicar uma migração:
1. Verifique os logs de erro
2. Restaure o backup se necessário
3. Execute `flask db current` para verificar a versão atual do banco

## Comandos Úteis Adicionais

- Verificar status das migrações:
  ```bash
  flask db current
  flask db history
  ```

- Marcar banco como atualizado sem aplicar migrações:
  ```bash
  flask db stamp head
  ```

## Contato

Se encontrar problemas ou tiver dúvidas sobre as migrações, entre em contato com a equipe de desenvolvimento.