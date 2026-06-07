with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Procura a linha exata
old_code = """    response = route_to_model(system_prompt, user_message, 'deepseek')
    return jsonify({"response": response})"""

new_code = """    response = route_to_model(system_prompt, user_message, 'deepseek')
    save_casulo_chat(expert_id, "user", user_message)
    save_casulo_chat(expert_id, "expert", response)
    return jsonify({"response": response})"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Código corrigido com sucesso!")
else:
    print("✗ Padrão não encontrado")
