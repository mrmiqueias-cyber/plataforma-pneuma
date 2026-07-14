import re

with open('instagram_automation.py', 'r', encoding='utf-8') as f:
    c = f.read()

alteracoes = []

# 1. METRICAS_PATH (se ainda não tem)
if 'METRICAS_PATH' not in c:
    c = c.replace(
        'scheduler = BackgroundScheduler(daemon=True)',
        'METRICAS_PATH = "metricas_instagram.json"\n\nscheduler = BackgroundScheduler(daemon=True)'
    )
    alteracoes.append("METRICAS_PATH adicionado")

# 2. Corrigir indentação do ultimo_erro e adicionar _salvar_metrica(sucesso)
if '_salvar_metrica(expert_nome, legenda, "sucesso")' not in c:
    c = c.replace(
        '_estado_automacao["ultimo_erro"] = None',
        '_estado_automacao["ultimo_erro"] = None\n            _salvar_metrica(expert_nome, legenda, "sucesso")'
    )
    alteracoes.append("_salvar_metrica(sucesso) adicionado")

# 3. _salvar_metrica(falha) nos dois lugares
if '_salvar_metrica(expert_nome, legenda, "falha")' not in c:
    c = c.replace(
        '_estado_automacao["ultimo_erro"] = "Falha ao criar post"\n            logger.error',
        '_estado_automacao["ultimo_erro"] = "Falha ao criar post"\n            _salvar_metrica(expert_nome, legenda, "falha")\n            logger.error'
    )
    c = c.replace(
        '_estado_automacao["ultimo_erro"] = str(e)\n        logger.error',
        '_estado_automacao["ultimo_erro"] = str(e)\n        _salvar_metrica(expert_nome, legenda, "falha")\n        logger.error'
    )
    alteracoes.append("_salvar_metrica(falha) adicionado")

with open('instagram_automation.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("OK! " + "; ".join(alteracoes))