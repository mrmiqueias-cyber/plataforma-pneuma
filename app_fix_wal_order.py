# Lê o app.py
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontra a linha "app = Flask(__name__)"
insert_index = None
for i, line in enumerate(lines):
    if 'app = Flask(__name__)' in line:
        insert_index = i + 1
        break

if insert_index:
    # Insere a ativação do WAL mode IMEDIATAMENTE após "app = Flask(__name__)"
    wal_code = """
# ✦ ATIVA WAL MODE ANTES DE QUALQUER ACESSO AO BANCO
import sqlite3
_db_path = 'casulo.db'
_conn = sqlite3.connect(_db_path)
_conn.execute('PRAGMA journal_mode=WAL')
_conn.execute('PRAGMA busy_timeout=5000')
_conn.execute('PRAGMA synchronous=NORMAL')
_conn.commit()
_conn.close()

"""
    lines.insert(insert_index, wal_code)

# Escreve de volta
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✓ WAL mode initialization movido para ANTES de qualquer acesso!")
