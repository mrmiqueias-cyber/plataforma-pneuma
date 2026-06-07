import os

# Lê o arquivo memoria_espiral.py
with open('memoria_espiral.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove o caminho_snapshot para desativar persistência em disco
content = content.replace(
    "memoria = MemoriaEspiral(caminho_snapshot='memoria_snapshot.json')",
    "memoria = MemoriaEspiral(caminho_snapshot=None)  # Desativado para evitar lock"
)

# Salva o arquivo modificado
with open('memoria_espiral.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ MemoriaEspiral desativada — snapshot removido!")
