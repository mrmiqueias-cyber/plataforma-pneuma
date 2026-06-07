import os

def modify_app_py(file_path='app.py'):
    if not os.path.exists(file_path):
        print(f'Error: {file_path} not found.')
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    in_expert_chat = False
    modified = False

    for i in range(len(lines)):
        line = lines[i]
        
        if '/expert/chat' in line:
            in_expert_chat = True
        
        if in_expert_chat and 'return jsonify({"response": response})' in line:
            indent = line[:line.find('return')]
            new_lines.append(f'{indent}save_casulo_chat(expert_id, "user", user_message)\n')
            new_lines.append(f'{indent}save_casulo_chat(expert_id, "expert", response)\n')
            modified = True
            in_expert_chat = False
        
        new_lines.append(line)

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print('File updated successfully.')
    else:
        print('Target line not found or already modified.')

if __name__ == '__main__':
    modify_app_py()
