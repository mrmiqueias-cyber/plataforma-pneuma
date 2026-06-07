import sqlite3
import os

db_path = 'casulo.db'

# Verifica o estado do banco
print("=== DIAGNÓSTICO DO BANCO ===\n")

# 1. Verifica se o banco existe
if os.path.exists(db_path):
    print(f"✓ Banco existe: {db_path}")
    print(f"✓ Tamanho: {os.path.getsize(db_path)} bytes")
else:
    print(f"✗ Banco NÃO existe: {db_path}")

# 2. Tenta conectar
try:
    conn = sqlite3.connect(db_path, timeout=10)
    print("✓ Conexão estabelecida")
    
    # 3. Verifica WAL mode
    cursor = conn.cursor()
    cursor.execute('PRAGMA journal_mode')
    journal_mode = cursor.fetchone()[0]
    print(f"✓ Journal mode: {journal_mode}")
    
    # 4. Verifica busy_timeout
    cursor.execute('PRAGMA busy_timeout')
    busy_timeout = cursor.fetchone()[0]
    print(f"✓ Busy timeout: {busy_timeout}ms")
    
    # 5. Verifica synchronous
    cursor.execute('PRAGMA synchronous')
    synchronous = cursor.fetchone()[0]
    print(f"✓ Synchronous: {synchronous}")
    
    # 6. Tenta uma query simples
    cursor.execute('SELECT 1')
    print("✓ Query simples funcionou")
    
    conn.close()
    print("\n✓ BANCO ESTÁ OK!")
    
except sqlite3.OperationalError as e:
    print(f"\n✗ ERRO: {e}")
    print("✗ O banco está TRAVADO ou CORROMPIDO!")
except Exception as e:
    print(f"\n✗ ERRO INESPERADO: {e}")
