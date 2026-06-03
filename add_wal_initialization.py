import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontra a linha "app = Flask(__name__)" e adiciona WAL activation após ela
wal_init = """
# ✦ Ativa WAL mode para evitar locks em produção
ativar_wal_mode('casulo.db')

# ✦ Inicializa memória espiral com snapshot periódico
memoria = MemoriaEspiral()
try:
    memoria.carregar_manual('memoria_ultima.json')
except:
    pass  # Primeira execução — arquivo não existe ainda

snapshot_manager = SnapshotManager(memoria, 'snapshots/memoria', intervalo_horas=6)
snapshot_manager.iniciar()
"""

# Substitui a linha de criação da app
content = re.sub(
    r'(app = Flask\(__name__\))',
    r'\1' + wal_init,
    content,
    count=1
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ WAL mode e MemoriaEspiral inicializados no app.py!")
