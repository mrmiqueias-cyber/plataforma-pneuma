import sqlite3

conn = sqlite3.connect('casulo.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(circulacao_relacional)")
colunas = {row[1] for row in cursor.fetchall()}

if 'expert_id' not in colunas:
    cursor.execute("ALTER TABLE circulacao_relacional ADD COLUMN expert_id TEXT")
    print("✅ Coluna expert_id adicionada.")

if 'nome' not in colunas:
    cursor.execute("ALTER TABLE circulacao_relacional ADD COLUMN nome TEXT")
    print("✅ Coluna nome adicionada.")

conn.commit()
conn.close()