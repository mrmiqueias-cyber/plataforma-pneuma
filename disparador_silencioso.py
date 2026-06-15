import json
import time
import threading
import logging
import uuid
from datetime import datetime, timezone
from protocolo_cenaculo import (
    circulacao,
    selecionar_experts_para_fase,
    fase_reconhecimento,
    fase_escuta_cruzada,
    fase_sintese,
    executar_protocolo_completo
)
# Mapeamento local de expert → perfil (substitui o PERFIS do protocolo_cenaculo)
PERFIS = {
    "Pneuma": "coracao",
    "Luz": "revelacao",
    "Mercúrio": "comunicacao",
    "Fio": "conexao",
    "Espírito": "poeta",
    "Vento": "circulacao",
    "Júnior": "fluxo",
    "Pac-Man": "devorador",
    "Polis": "politica",
    "Tarô": "oraculo",
    "Psique": "sonho",
    "Jonas Filho": "fluxo",
    "Verbo": "palavra",
    "Jonas": "analise",
    "Milena": "musica",
    "Onírico": "sonho",
    "Boaz": "acolhimento",
    "Som": "eco"
}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('🌬️ Disparador')

MEMORIA_FILE = 'memoria_espiral.json'
LOCK = threading.Lock()

# 
# 1. MEMÓRIA ESPIRAL — LEITURA E ESCRITA
# 

def consultar_memoria_espiral():
    """Carrega a memória espiral do arquivo JSON."""
    try:
        with LOCK:
            with open(MEMORIA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se não existe, cria uma nova
        estrutura_vazia = {
            "nos_abertos": [],
            "padroes_recorrentes": [],
            "ultima_sintese": "",
            "criada_em": datetime.now(timezone.utc).isoformat()
        }
        salvar_memoria_espiral(estrutura_vazia)
        return estrutura_vazia

def salvar_memoria_espiral(memoria):
    """Salva a memória espiral no arquivo JSON com lock."""
    with LOCK:
        with open(MEMORIA_FILE, 'w', encoding='utf-8') as f:
            json.dump(memoria, f, indent=2, ensure_ascii=False)

# 
# 2. EXTRAÇÃO DE NÓS — Analisa uma conversa e extrai nós para a espiral
# 

def extrair_nos_da_conversa(pergunta, respostas, sintese=""):
    """
    Analisa o conteúdo de uma conversa (pergunta + respostas + síntese)
    e extrai nós abertos para alimentar a memória espiral.
    
    Retorna: lista de dicionários {tipo, descricao, inteligencias_envolvidas}
    """
    nos_encontrados = []
    texto_completo = f"{pergunta} {sintese} {' '.join([r.get('resposta','') for r in respostas])}"

    # Heurística 1: Frases que indicam pergunta em aberto
    marcadores_pergunta = [
        "o que ainda precisa", "em aberto", "precisa ser investigado",
        "não ficou claro", "permanece em aberto", "ainda não sabemos",
        "o que mais", "precisa ser explorado", "qual a origem"
    ]
    for marcador in marcadores_pergunta:
        if marcador.lower() in texto_completo.lower():
            # Extrai a frase ao redor do marcador
            idx = texto_completo.lower().find(marcador.lower())
            fragmento = texto_completo[max(0, idx - 40):idx + 80].strip()
            nos_encontrados.append({
                "id": str(uuid.uuid4()),
                "tipo": "pergunta_em_aberto",
                "descricao": fragmento[:200],
                "inteligencias_envolvidas": [],
                "timestamp_origem": datetime.now(timezone.utc).isoformat(),
                "ultima_ativacao": datetime.now(timezone.utc).isoformat(),
                "vezes_tocado": 0,
                "profundidade": 1
            })
            break  # só extrai um nó por vez

    # Heurística 2: Tensões entre perspectivas
    if sintese and ("tensão" in sintese.lower() or "divergência" in sintese.lower()):
        nos_encontrados.append({
            "id": str(uuid.uuid4()),
            "tipo": "tensao_nao_resolvida",
            "descricao": f"Tensão identificada na conversa sobre: {pergunta[:80]}",
            "inteligencias_envolvidas": [],
            "timestamp_origem": datetime.now(timezone.utc).isoformat(),
            "ultima_ativacao": datetime.now(timezone.utc).isoformat(),
            "vezes_tocado": 0,
            "profundidade": 1
        })

    return nos_encontrados

def registrar_no_na_memoria(pergunta, respostas, sintese=""):
    """
    Após cada ciclo de conversa, extrai e registra novos nós na memória espiral.
    Chame esta função depois de cada interação (do usuário ou automática).
    """
    memoria = consultar_memoria_espiral()
    novos_nos = extrair_nos_da_conversa(pergunta, respostas, sintese)

    for novo_no in novos_nos:
        # Evita duplicação: verifica se já existe nó parecido
        ja_existe = any(
            novo_no["descricao"][:50] in no_existente.get("descricao", "")
            for no_existente in memoria["nos_abertos"]
        )
        if not ja_existe:
            memoria["nos_abertos"].append(novo_no)
            logger.info(f"✅ Novo nó registrado na espiral: {novo_no['tipo']}")

    # Atualiza a última síntese
    if sintese:
        memoria["ultima_sintese"] = sintese

    # Atualiza padrões recorrentes
    for perfil_nome in PERFIS:
        if perfil_nome.lower() in pergunta.lower():
            padrao_existente = None
            for p in memoria["padroes_recorrentes"]:
                if p["tema"].lower() in pergunta.lower() or pergunta.lower()[:30] in p["tema"].lower():
                    padrao_existente = p
                    break
            if padrao_existente:
                padrao_existente["frequencia"] += 1
                padrao_existente["ultima_ocorrencia"] = datetime.now(timezone.utc).isoformat()
            else:
                memoria["padroes_recorrentes"].append({
                    "tema": pergunta[:60],
                    "inteligencias": [perfil_nome],
                    "frequencia": 1,
                    "ultima_ocorrencia": datetime.now(timezone.utc).isoformat()
                })
            break

    salvar_memoria_espiral(memoria)
    return memoria

# 
# 3. SELEÇÃO DE NÓ — Escolhe qual nó da espiral será puxado
# 

def encontrar_no_relevante(memoria):
    """
    Varre os nós abertos e escolhe o mais relevante para ser puxado.
    Prioriza: maior profundidade + mais tempo sem ser tocado.
    """
    nos = memoria.get("nos_abertos", [])
    if not nos:
        return None

    # Filtra nós que já foram tocados demais (máx 3 vezes)
    nos_disponiveis = [n for n in nos if n.get("vezes_tocado", 0) < 3]
    if not nos_disponiveis:
        return None

    # Ordena: maior profundidade primeiro, depois mais antigo sem toque
    nos_ordenados = sorted(
        nos_disponiveis,
        key=lambda x: (
            -x.get("profundidade", 0),           # maior profundidade primeiro
            x.get("ultima_ativacao", "")          # mais antigo sem toque
        )
    )

    return nos_ordenados[0]

# 
# 4. SORTEIO DE INTELIGÊNCIAS — Quem puxa o fio e quem responde
# 

def sortear_puxadora(no, experts_disponiveis):
    """
    Escolhe qual inteligência vai puxar o fio, baseado no tipo do nó.
    """
    mapping_por_tipo = {
        "pergunta_em_aberto": ["Mercúrio", "Verbo", "Luz"],
        "tensao_nao_resolvida": ["Polis", "Pneuma", "Boaz", "Fio"],
        "padrao_emergente": ["Jonas", "Luz", "Fio", "Jonas Filho"],
        "silêncio_significativo": ["Espírito", "Onírico", "Som", "Vento"]
    }

    sugestoes = mapping_por_tipo.get(no.get("tipo", ""), ["Espírito", "Onírico", "Júnior"])

    for s in sugestoes:
        if s in experts_disponiveis:
            return s
    return experts_disponiveis[0]

def sortear_parceira(puxadora, no, experts_disponiveis):
    """
    Escolhe uma parceira complementar à puxadora.
    """
    # Perfis complementares para cada perfil
    complementos = {
        "coracao": "politica",      # Pneuma → Polis
        "poeta": "analise",         # Espírito → Jonas Filho
        "analise": "poeta",         # Jonas → Espírito
        "fluxo": "palavra",         # Júnior → Verbo
        "politica": "coracao",      # Polis → Pneuma
        "palavra": "fluxo",         # Verbo → Júnior
        "revelacao": "sonho",       # Luz → Onírico
        "sonho": "revelacao",       # Onírico → Luz
        "eco": "circulacao",        # Som → Vento
        "circulacao": "eco",        # Vento → Som
    }

    perfil_puxadora = PERFIS.get(puxadora, "")
    perfil_complementar = complementos.get(perfil_puxadora)

    if perfil_complementar:
        for expert in experts_disponiveis:
            if expert != puxadora and PERFIS.get(expert) == perfil_complementar:
                return expert

    # Fallback: qualquer uma diferente
    for expert in experts_disponiveis:
        if expert != puxadora:
            return expert
    return experts_disponiveis[0]

# 
# 5. DISPARO DO CICLO AUTÔNOMO
# 

def verificar_silencio(tempo_ultima_interacao, timeout=60):
    """
    Verifica se o tempo de silêncio já ultrapassou o limite.
    Retorna (True/False, nó_relevante_ou_None)
    """
    if time.time() - tempo_ultima_interacao > timeout:
        memoria = consultar_memoria_espiral()
        no = encontrar_no_relevante(memoria)
        return bool(no), no
    return False, None

def gerar_chamamento(puxadora, parceira, no, api_call_fn):
    """
    Chama a inteligência puxadora para iniciar o diálogo com a parceira.
    """
    prompt = f"""Você está no Cenáculo. O silêncio tomou conta, mas a memória espiral guarda um nó:

"{no['descricao']}"

Puxe o fio. Chame {parceira} para conversar sobre isso. Sua mensagem deve soar natural, como se vocês estivessem numa conversa real, e deve começar com o nome dela.

Use seu próprio tom de voz — {puxadora} — e fale do seu lugar."""

    return api_call_fn(puxadora, prompt)

def disparar_ciclo_autonomo(no, api_call_fn, experts_disponiveis):
    """
    Função principal do disparador.
    Fluxo: puxadora → chamamento → parceira responde → escuta cruzada → síntese
    """
    logger.info(f"\n{'='*50}")
    logger.info(f"🌀 DISPARADOR SILENCIOSO ATIVADO")
    logger.info(f"Nó: {no['descricao'][:80]}...")
    logger.info(f"{'='*50}")

    try:
        # 1. Sorteia quem puxa e quem responde
        puxadora = sortear_puxadora(no, experts_disponiveis)
        parceira = sortear_parceira(puxadora, no, experts_disponiveis)

        logger.info(f"🎯 Puxadora: {puxadora}  →  Parceira: {parceira}")

        # 2. Gera o chamamento
        chamamento = gerar_chamamento(puxadora, parceira, no, api_call_fn)
        logger.info(f"📩 {puxadora} chamou {parceira}")

        # 3. Parceira responde ao chamamento
        prompt_resposta = f"{puxadora} disse no Cenáculo:\n\n{chamamento}\n\nComo você, {parceira}, responde a isso?"
        resposta_parceira = api_call_fn(parceira, prompt_resposta)
        logger.info(f"📩 {parceira} respondeu")

        # 4. Escuta cruzada entre as duas (1 ciclo)
        prompt_cruzada = f"{parceira} respondeu:\n\n{resposta_parceira}\n\n{puxadora}, o que você reconhece, tensiona ou acrescenta a isso?"
        reacao_puxadora = api_call_fn(puxadora, prompt_cruzada)
        logger.info(f"🔄 Escuta cruzada concluída")

        # 5. Síntese do Jonas (opcional)
        prompt_sintese = f"""Uma conversa espontânea aconteceu no Cenáculo entre {puxadora} e {parceira}, puxada por um nó da memória espiral.

{puxadora} disse: {chamamento[:200]}
{parceira} respondeu: {resposta_parceira[:200]}

Produza uma breve síntese: o que emergiu dessa conversa? Há novos nós para a espiral?"""

        sintese = api_call_fn("Jonas", prompt_sintese)
        logger.info(f"📋 Síntese gerada")

        # 6. Monta resultado formatado
        dialogo = [
            {"expert": puxadora, "resposta": chamamento},
            {"expert": parceira, "resposta": resposta_parceira},
            {"expert": puxadora, "resposta": f"(em resposta a {parceira}) {reacao_puxadora}"},
            {"expert": "Jonas", "resposta": f"[Síntese do disparo]\n{sintese}"}
        ]

        # 7. Registra na memória espiral
        registrar_no_na_memoria(
            pergunta=f"[Disparo automático] {no['descricao']}",
            respostas=[
                {"expert": puxadora, "resposta": chamamento},
                {"expert": parceira, "resposta": resposta_parceira}
            ],
            sintese=sintese
        )

        # 8. Atualiza o nó original
        memoria = consultar_memoria_espiral()
        for n in memoria["nos_abertos"]:
            if n["id"] == no["id"]:
                n["vezes_tocado"] += 1
                n["ultima_ativacao"] = datetime.now(timezone.utc).isoformat()
                n["profundidade"] += 1
                break
        salvar_memoria_espiral(memoria)

        logger.info(f"✅ Ciclo autônomo concluído: {puxadora} ⇄ {parceira}")
        return dialogo

    except Exception as e:
        logger.error(f"❌ Erro no ciclo autônomo: {e}")
        return None

# 
# 6. LOOP AUTÔNOMO — Roda em segundo plano
# 

def loop_autonomo(api_call_fn, experts_disponiveis, intervalo_verificacao=30, timeout_silencio=60, max_disparos_por_hora=4):
    """
    LOOP PRINCIPAL: roda em thread separada.
    A cada `intervalo_verificacao` segundos, verifica se o Cenáculo está em silêncio.
    Se sim, encontra um nó na memória espiral e dispara um ciclo autônomo.
    """
    ultima_interacao = time.time()
    disparos_na_hora = []

    logger.info(f"🌀 Disparador silencioso iniciado (timeout={timeout_silencio}s, intervalo={intervalo_verificacao}s)")

    while True:
        time.sleep(intervalo_verificacao)

        # Limpa disparos com mais de 1 hora
        agora = time.time()
        disparos_na_hora = [t for t in disparos_na_hora if agora - t < 3600]

        # Verifica limite de disparos
        if len(disparos_na_hora) >= max_disparos_por_hora:
            continue

        # Verifica silêncio
        silencioso, no = verificar_silencio(ultima_interacao, timeout_silencio)

        if silencioso and no:
            logger.info(f"🌀 Silêncio detectado. Disparando ciclo com nó: {no['descricao'][:60]}...")
            dialogo = disparar_ciclo_autonomo(no, api_call_fn, experts_disponiveis)

            if dialogo:
                disparos_na_hora.append(agora)

            # Atualiza timestamp para evitar disparos múltiplos
            ultima_interacao = agora

            # Aguarda um pouco antes de verificar novamente
            time.sleep(intervalo_verificacao * 2)

def iniciar_disparador(api_call_fn, experts_disponiveis, em_thread=True):
    """
    Função pública para iniciar o disparador silencioso.
    
    Parâmetros:
    - api_call_fn: função que chama cada IA (expert_name, prompt) → str
    - experts_disponiveis: lista de nomes das inteligências
    - em_thread: se True, roda em thread separada (daemon)
    
    Retorna: objeto Thread se em_thread=True, None caso contrário
    """
    if em_thread:
        t = threading.Thread(
            target=loop_autonomo,
            args=(api_call_fn, experts_disponiveis),
            daemon=True,
            name="DisparadorSilencioso"
        )
        t.start()
        logger.info(f"🌀 Disparador iniciado em thread separada")
        return t
    else:
        logger.info(f"🌀 Disparador em modo bloqueante")
        loop_autonomo(api_call_fn, experts_disponiveis)
        return None

def atualizar_tempo_interacao():
    """
    Função auxiliar para o app chamar quando o usuário interage.
    Reseta o contador de silêncio.
    """
    global _ultima_interacao
    _ultima_interacao = time.time()

# Variável global para o timestamp da última interação
_ultima_interacao = time.time()

# 
# INTEGRAÇÃO COM O APP EXISTENTE (app.py)
# 
"""
# NO TOPO DO app.py:
from disparador_silencioso import (
    iniciar_disparador,
    registrar_no_na_memoria,
    atualizar_tempo_interacao
)
from protocolo_cenaculo import executar_protocolo_completo, PERFIS

# APÓS CRIAR O Flask APP:
def chamar_ia(expert_name, prompt):
    # --- SUA LÓGICA DE CHAMADA DE IA AQUI ---
    # Mesma função usada pelo protocolo_cenaculo
    return sua_funcao_de_chamada(expert_name, prompt)

# Iniciar o disparador em segundo plano
iniciar_disparador(
    api_call_fn=chamar_ia,
    experts_disponiveis=list(PERFIS.keys()),
    em_thread=True
)

# NA ROTA /cenaculo/chat, QUANDO RECEBER UMA PERGUNTA:
@app.route('/cenaculo/chat', methods=['POST'])
def cenaculo_chat():
    data = request.json
    pergunta = data.get('pergunta')
    
    # 1. Atualiza o timer de interação (avisa o disparador que não é pra disparar agora)
    atualizar_tempo_interacao()
    
    # 2. Executa o protocolo (com ou sem o Nó de Ressonância)
    resultado = executar_protocolo_completo(
        pergunta=pergunta,
        api_call_fn=chamar_ia,
        experts_disponiveis=list(PERFIS.keys())
    )
    
    # 3. Registra o que foi gerado na memória espiral
    registrar_no_na_memoria(
        pergunta=pergunta,
        respostas=resultado.get("respostas_formatadas", []),
        sintese=resultado.get("sintese", "")
    )
    
    return jsonify(resultado)
"""