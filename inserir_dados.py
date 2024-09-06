import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('processos.db')
cursor = conn.cursor()

# Inserir um registro de teste na tabela 'processos' com um ID diferente
cursor.execute('''
    INSERT INTO processos (id, nivel_sigilo, orgao_julgador_nome, municipio_ibge, codigo_movimento, nome_movimento, data_hora_movimento, codigo_assunto, nome_assunto)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    '0023456-89.2021.8.17.0002',  # ID do processo diferente
    0,                            # Nível de sigilo
    'Homicídio Qualificado',      # Classe (órgão julgador)
    2613008,                      # Código IBGE do município
    12345,                        # Código do movimento
    'Movimento de Teste',         # Nome do movimento
    '2023-11-20 10:15:00',        # Data do movimento
    3632,                         # Código do assunto
    'Crimes de Trânsito'          # Nome do assunto
))

# 

