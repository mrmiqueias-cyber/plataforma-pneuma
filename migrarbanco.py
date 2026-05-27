import sqlite3, os, sys
from datetime import datetime

conn = sqlite3.connect('casulo.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(experts)")
colunas = [col[1] for col in cursor.fetchall()]

if 'is_fixed' not in colunas:
    cursor.execute("ALTER TABLE experts ADD COLUMN is_fixed INTEGER DEFAULT 0")
    print("✅ Coluna 'is_fixed' adicionada.")
else:
    print("✅ Coluna 'is_fixed' já existe.")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='circulacao_relacional'")
if not cursor.fetchone():
    cursor.execute("""CREATE TABLE circulacao_relacional (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inteligencia_id TEXT, dna TEXT, frequencia REAL,
        verso TEXT, timestamp DATETIME, outras_inteligencias_presentes TEXT
    )""")
    print("✅ Tabela 'circulacao_relacional' criada.")
else:
    print("✅ Tabela 'circulacao_relacional' já existe.")

conn.commit()

print("\n=== TABELAS ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for t in cursor.fetchall(): print(f"  - {t[0]}")

print("\n=== COLUNAS DA TABELA experts ===")
cursor.execute("PRAGMA table_info(experts)")
for c in cursor.fetchall(): print(f"  - {c[1]} ({c[2]})")

conn.close()
print("\nMigração concluída!")