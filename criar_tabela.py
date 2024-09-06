import sqlite3

# Conectar ao banco de dados (cria o arquivo se não existir)
conn = sqlite3.connect('processos.db')

# Criar um cursor para executar comandos SQL
cursor = conn.cursor()

# Criar a tabela 'processos' se ainda não existir
cursor.execute('''
    CREATE TABLE IF NOT EXISTS processos (
        id TEXT PRIMARY KEY,
        nivel_sigilo INTEGER,
        orgao_julgador_nome TEXT,
        municipio_ibge INTEGER,
        codigo_movimento INTEGER,
        nome_movimento TEXT,
        data_hora_movimento TEXT,
        codigo_assunto INTEGER,
        nome_assunto TEXT
    )
''')

# Confirmar as alterações no banco de dados
conn.commit()

# Fechar a conexão com o banco de dados
conn.close()

print("Tabela 'processos' criada com sucesso (se ainda não existia).")
