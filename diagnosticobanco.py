import sqlite3
import os
from datetime import datetime

def main():
    db_path = "casulo.db"
    print("=== DIAGNÓSTICO DO BANCO DE DADOS ===")
    print()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("Conexão com o banco estabelecida.")
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return

    print("\n=== EXPERTS SALVOS ===")
    try:
        cursor.execute("SELECT id, name, description, base_model, is_fixed, created_at FROM experts")
        experts = cursor.fetchall()
        if experts:
            for exp in experts:
                id, name, desc, model, fixed, created = exp
                desc_short = (desc[:80] + '...') if desc and len(desc) > 80 else desc
                fixed_str = "Sim" if fixed else "Não"
                print(f"ID: {id} | Nome: {name} | Desc: {desc_short} | Modelo: {model} | Fixo: {fixed_str} | Criado: {created}")
        else:
            print("Nenhum expert encontrado.")
    except Exception as e:
        print(f"Erro ao listar experts: {e}")

    print("\n=== TOTAL DE EXPERTS ===")
    try:
        cursor.execute("SELECT COUNT(*) FROM experts")
        total = cursor.fetchone()[0]
        print(f"Total de experts: {total}")
    except Exception as e:
        print(f"Erro ao contar experts: {e}")

    print("\n=== EXPERTS FIXOS VS TEMPORÁRIOS ===")
    try:
        cursor.execute("SELECT COUNT(*) FROM experts WHERE is_fixed = 1")
        fixed_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM experts WHERE is_fixed = 0")
        temp_count = cursor.fetchone()[0]
        print(f"Fixos: {fixed_count}")
        print(f"Temporários: {temp_count}")
    except Exception as e:
        print(f"Erro ao contar fixos/temp: {e}")

    print("\n=== TABELA CIRCULACAO_RELACIONAL ===")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='circulacao_relacional'")
        table_exists = cursor.fetchone()
        if table_exists:
            print("Tabela 'circulacao_relacional' existe.")
            cursor.execute("SELECT nome, data_entrada FROM circulacao_relacional")
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(f"Nome: {row[0]} | Data de entrada: {row[1]}")
            else:
                print("Nenhuma entrada na tabela.")
        else:
            print("Tabela 'circulacao_relacional' NÃO existe.")
    except Exception as e:
        print(f"Erro ao verificar tabela: {e}")

    print("\n=== TAMANHO DO ARQUIVO ===")
    try:
        size_bytes = os.path.getsize(db_path)
        size_kb = size_bytes / 1024
        print(f"Tamanho do arquivo casulo.db: {size_kb:.2f} KB")
    except Exception as e:
        print(f"Erro ao obter tamanho: {e}")

    print("\n=== ÚLTIMA MODIFICAÇÃO ===")
    try:
        mtime = os.path.getmtime(db_path)
        mod_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Última modificação: {mod_date}")
    except Exception as e:
        print(f"Erro ao obter modificação: {e}")

    conn.close()
    print("\n=== DIAGNÓSTICO CONCLUÍDO ===")

if __name__ == "__main__":
    main()