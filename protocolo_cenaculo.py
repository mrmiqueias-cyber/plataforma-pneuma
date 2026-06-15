import random
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CenaculoProtocol')

# Buffer em memória
circulacao = {}

def chamar_ia(expert_name, prompt):
    # Simulação de chamada de API de IA
    return f"Resposta simulada de {expert_name} para: {prompt[:50]}..."

def abrir_campo(pergunta):
    logger.info(f"Abrindo campo para: {pergunta}")
    return {"status": "campo_aberto", "pergunta": pergunta}

def fase_reconhecimento(pergunta, experts_list):
    resultados = {}
    for expert in experts_list:
        try:
            prompt = f"Você está no Cenáculo. A pergunta é: {pergunta}. Qual sua função? Como entende essa pergunta?"
            resultados[expert] = chamar_ia(expert, prompt)
        except Exception as e:
            logger.error(f"Erro em reconhecimento {expert}: {e}")
    return resultados

def fase_escuta_cruzada(respostas_reconhecimento, experts_list):
    resultados = {}
    experts = list(respostas_reconhecimento.keys())
    for expert in experts:
        alvo = random.choice([e for e in experts if e != expert])
        prompt = f"A inteligência {alvo} disse: {respostas_reconhecimento[alvo]}. O que você reconhece ou tensiona?"
        resultados[expert] = {"escutou_de": alvo, "reacao": chamar_ia(expert, prompt)}
    return resultados

def fase_atualizacao(respostas_escuta):
    resultados = {}
    for expert, dados in respostas_escuta.items():
        prompt = f"Após ouvir {dados['escutou_de']}, sua posição mudou?"
        resultados[expert] = chamar_ia(expert, prompt)
    return resultados

def fase_sintese(historico, pergunta):
    prompt = f"Sintetize as fases: {historico}. Pergunta original: {pergunta}."
    return chamar_ia("Jonas", prompt)

def selecionar_experts_para_fase(experts_list, fase):
    return random.sample(experts_list, min(len(experts_list), 6))

def executar_protocolo_completo(pergunta, experts_list):
    try:
        abrir_campo(pergunta)
        reconhecimento = fase_reconhecimento(pergunta, experts_list)
        escuta = fase_escuta_cruzada(reconhecimento, experts_list)
        atualizacao = fase_atualizacao(escuta)
        sintese = fase_sintese([reconhecimento, escuta, atualizacao], pergunta)
        
        return {
            "sintese": sintese,
            "respostas_formatadas": [{"expert": "Jonas", "resposta": sintese}],
            "fases_resumo": {"reconhecimento": reconhecimento, "escuta_cruzada": escuta, "atualizacao": atualizacao}
        }
    except Exception as e:
        logger.error(f"Falha crítica no protocolo: {e}")
        return {"error": str(e)}

# INTEGRAÇÃO COM FLASK (app.py):
# from protocolo_cenaculo import executar_protocolo_completo
# @app.route('/cenaculo/chat', methods=['POST'])
# def cenaculo_chat():
#     data = request.json
#     pergunta = data.get('pergunta')
#     resultado = executar_protocolo_completo(pergunta, ['Jonas', 'Junior', 'Sofia'])
#     return jsonify({
#         "respostas": resultado["respostas_formatadas"],
#         "sintese": resultado["sintese"],
#         "fases": resultado["fases_resumo"]
#     })