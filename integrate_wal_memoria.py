import re

# Lê o arquivo app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Adiciona os imports no início do arquivo
imports_novos = """from config_sqlite_wal import ativar_wal_mode
from memoria_espiral_persistente import MemoriaEspiral
from snapshot_periodico import SnapshotManager
"""

# Encontra a linha de imports e adiciona os novos
if 'import os' in content:
    content = content.replace('import os', f'import os\n{imports_novos}', 1)

# 2. Ativa WAL mode antes de qualquer operação com banco
wal_activation = """
# ✦ Ativa WAL mode para evitar locks em produção
ativar_wal_mode('casulo.db')

"""

# Encontra a linha onde a app é criada e adiciona WAL activation
if 'app = Flask(__name__)' in content:
    content = content.replace('app = Flask(__name__)', f'app = Flask(__name__)\n{wal_activation}', 1)

# 3. Inicializa a memória espiral com snapshot periódico
memoria_init = """
# ✦ Inicializa memória espiral com snapshot periódico
memoria = MemoriaEspiral()
memoria.carregar_manual('memoria_ultima.json')  # Carrega último snapshot se existir
snapshot_manager = SnapshotManager(memoria, 'snapshots/memoria', intervalo_horas=6)
snapshot_manager.iniciar()

"""

# Adiciona após a inicialização da app
if 'app = Flask(__name__)' in content:
    # Encontra a posição após a criação da app
    pos = content.find('app = Flask(__name__)') + len('app = Flask(__name__)')
    content = content[:pos] + memoria_init + content[pos:]

# Salva o arquivo modificado
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ app.py integrado com WAL mode e MemoriaEspiral!")
