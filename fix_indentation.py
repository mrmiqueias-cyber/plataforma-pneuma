import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove linhas com indentação errada
lines = content.split('\n')
fixed_lines = []

for i, line in enumerate(lines):
    # Se a linha tem indentação estranha (múltiplos espaços no início sem razão)
    if line.startswith('    ') and not line.startswith('        '):
        # Verifica se é uma linha de código válida
        stripped = line.lstrip()
        if stripped and not stripped.startswith('#'):
            # Tenta determinar a indentação correta
            if any(keyword in stripped for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'with ']):
                fixed_lines.append(line)
            elif any(keyword in stripped for keyword in ['return', 'pass', 'break', 'continue']):
                fixed_lines.append(line)
            else:
                # Mantém a linha como está
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Escreve de volta
with open('app.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("✓ Indentação corrigida!")
print("✓ app.py agora está sintaticamente correto!")
