import sqlite3
import os

# Força a ativação do WAL mode ANTES de qualquer outra coisa
db_path = 'casulo.db'

# Se o banco não existe, cria ele
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.close()

# Agora ativa WAL mode
conn = sqlite3.connect(db_path)
conn.execute('PRAGMA journal_mode=WAL')
conn.execute('PRAGMA busy_timeout=5000')
conn.execute('PRAGMA synchronous=NORMAL')
conn.commit()
conn.close()

print("✓ WAL mode ativado com sucesso!")
print("✓ Busy timeout: 5000ms")
print("✓ Synchronous: NORMAL")
