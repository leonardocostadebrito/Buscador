import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('processos.db')
cursor = conn.cursor()

# Verificar os registros da 1ª Vara da Comarca de São Bento do Una
cursor.execute("SELECT * FROM processos WHERE LOWER(orgao_julgador_nome) LIKE ?", ('%1ª vara da comarca de são bento do una%',))

# Buscar todos os resultados
resultados = cursor.fetchall()

# Exibir os resultados
if resultados:
    for resultado in resultados:
        print(resultado)
else:
    print("Nenhum dado encontrado para a 1ª Vara da Comarca de São Bento do Una.")

# Fechar a conexão com o banco de dados
conn.close()
