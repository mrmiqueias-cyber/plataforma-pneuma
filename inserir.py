with open('dashboard_funcs.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

with open('instagram_automation.py', 'r', encoding='utf-8') as f:
    c = f.read()

insert_pos = c.find('\ndef init_app(app):')
if insert_pos > 0:
    c = c[:insert_pos] + '\n' + codigo + c[insert_pos:]
    with open('instagram_automation.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Dashboard adicionado com sucesso!")
else:
    print("ERRO: nao encontrei 'def init_app(app)' no arquivo")