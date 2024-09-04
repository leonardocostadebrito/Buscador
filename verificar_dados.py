import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('processos.db')
cursor = conn.cursor()

# Verificar se há registros com a classe "Homicídio Qualificado"
cursor.execute("SELECT * FROM processos WHERE LOWER(orgao_julgador_nome) LIKE ?", ('%homicídio qualificado%',))

# Buscar todos os resultados
resultados = cursor.fetchall()

# Exibir os resultados
if resultados:
    for resultado in resultados:
        print(resultado)
else:
    print("Nenhum dado encontrado para 'Homicídio Qualificado'.")

# Fechar a conexão com o banco de dados
conn.close()
