import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('instance/gestao.db')
cursor = conn.cursor()

# Executar o DELETE
cursor.execute('DELETE FROM sale WHERE client_id LIKE "%1%"')

# Commit das alterações e mostrar número de registros afetados
conn.commit()
print('Registros deletados:', cursor.rowcount)

# Fechar a conexão
conn.close()