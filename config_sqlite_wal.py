import sqlite3

def ativar_wal_mode(caminho_banco):
    """Ativa WAL mode no SQLite para evitar locks em produção."""
    try:
        conn = sqlite3.connect(caminho_banco)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=5000')
        conn.commit()
        conn.close()
        print(f"✓ WAL mode ativado em {caminho_banco}")
    except Exception as e:
        print(f"✗ Erro ao ativar WAL: {e}")

if __name__ == '__main__':
    ativar_wal_mode('casulo.db')
