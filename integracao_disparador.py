import logging
from cenaculo_bp import INTELIGENCIAS, route_to_model, reforçar_identidade
from disparador_silencioso import (
    iniciar_disparador,
    registrar_no_na_memoria,
    atualizar_tempo_interacao
)

logger = logging.getLogger('IntegracaoDisparador')

def chamar_ia(expert_name, prompt):
    """Função-ponte: adapta (expert_name, prompt) → route_to_model() real"""
    for eid, config in INTELIGENCIAS.items():
        if config["nome"].lower() == expert_name.lower():
            try:
                system_prompt = reforçar_identidade(
                    config["system_prompt"], config["nome"],
                    config["emoji"], config["exemplo"]
                )
                return route_to_model(
                    system_prompt, prompt, 'deepseek',
                    temperature=config["temperatura"]
                )
            except Exception as e:
                logger.error(f"Erro ao chamar {expert_name}: {e}")
                return f"{config['emoji']} **{config['nome']}:** (comunicação interrompida)"
    
    logger.warning(f"Expert '{expert_name}' não encontrado em INTELIGENCIAS")
    return f"**{expert_name}:** Não encontrado entre as inteligências."

EXPERTS_DISPONIVEIS = [config["nome"] for config in INTELIGENCIAS.values()]

def iniciar_disparador_autonomo():
    """Inicia o disparador silencioso em thread separada"""
    logger.info("🌀 Iniciando disparador silencioso...")
    try:
        thread = iniciar_disparador(
            api_call_fn=chamar_ia,
            experts_disponiveis=EXPERTS_DISPONIVEIS,
            em_thread=True
        )
        logger.info("✅ Disparador silencioso ativo!")
        return thread
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar disparador: {e}")
        return None

registrar_na_memoria = registrar_no_na_memoria
avisar_interacao = atualizar_tempo_interacao

# ═══════════════════════════════════════════
# COMO USAR NO app.py:
# ═══════════════════════════════════════════
# 
# 1. No TOPO do app.py, COLOQUE:
#    from integracao_disparador import iniciar_disparador_autonomo, registrar_na_memoria, avisar_interacao
# 
# 2. LOGO APÓS criar o Flask app (app = Flask(...)), COLOQUE:
#    iniciar_disparador_autonomo()
# 
# 3. DENTRO da rota /cenaculo/chat, ANTES de processar:
#    avisar_interacao()
#    # ... executa o protocolo ...
#    resultado = executar_protocolo_completo(pergunta)
#    registrar_na_memoria(
#        pergunta=pergunta,
#        respostas=resultado.get("respostas_formatadas", []),
#        sintese=resultado.get("sintese", "")
#    )
# ═══════════════════════════════════════════