import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove TODAS as linhas que começam com espaços extras desnecessários
fixed_lines = []
for line in lines:
    # Se a linha tem indentação, verifica se é válida
    if line.startswith(' '):
        # Conta os espaços
        spaces = len(line) - len(line.lstrip(' '))
        
        # Se tem indentação que não é múltiplo de 4, remove
        if spaces % 4 != 0:
            # Remove os espaços extras
            fixed_lines.append(line.lstrip())
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Escreve de volta
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✓ Todas as indentações foram corrigidas!")
print("✓ Apenas indentações válidas (múltiplos de 4) foram mantidas!")
