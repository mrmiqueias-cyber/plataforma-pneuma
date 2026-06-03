import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontra a seção de imports e adiciona lock para sincronizar acesso
lock_code = """
import threading
_db_lock = threading.Lock()
"""

# Insere o lock LOGO APÓS os imports
if 'import threading' not in content:
    # Encontra o último import
    last_import = max(
        content.rfind('import '),
        content.rfind('from ')
    )
    # Encontra o final da linha
    end_of_line = content.find('\n', last_import)
    content = content[:end_of_line+1] + lock_code + content[end_of_line+1:]

# Agora modifica a inicialização da MemoriaEspiral para usar o lock
old_memoria = "memoria = MemoriaEspiral()"
new_memoria = """with _db_lock:
    memoria = MemoriaEspiral()"""

content = content.replace(old_memoria, new_memoria)

# Modifica a inicialização do SnapshotManager
old_snapshot = "snapshot_manager = SnapshotManager("
new_snapshot = """with _db_lock:
    snapshot_manager = SnapshotManager("""

content = content.replace(old_snapshot, new_snapshot)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Lock de sincronização adicionado!")
print("✓ Acesso ao banco agora é serializado!")
