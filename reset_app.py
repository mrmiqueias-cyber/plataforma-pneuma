# Vamos fazer um reset completo do app.py
# Removendo TODAS as linhas com indentação errada

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Filtra apenas linhas com indentação válida (múltiplos de 4)
fixed_lines = []
for line in lines:
    # Conta espaços no início
    stripped = line.lstrip(' ')
    spaces = len(line) - len(stripped)
    
    # Se tem espaços, verifica se é múltiplo de 4
    if spaces > 0:
        if spaces % 4 == 0:
            fixed_lines.append(line)
        # Se não é múltiplo de 4, remove os espaços extras
        else:
            # Calcula quantos espaços DEVERIA ter
            correct_spaces = (spaces // 4) * 4
            fixed_lines.append(' ' * correct_spaces + stripped)
    else:
        fixed_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✓ app.py foi resetado com indentação corrigida!")
print("✓ Todas as linhas agora têm indentação válida (múltiplos de 4)!")
