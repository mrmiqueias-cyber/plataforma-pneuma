import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cache global dos experts
EXPERTS_CACHE = None
CACHE_LOCK = threading.Lock()

def load_experts_cache():
    global EXPERTS_CACHE
    with CACHE_LOCK:
        if EXPERTS_CACHE is None:
            conn = sqlite3.connect('casulo.db', timeout=10.0)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT id, name, description, instructions, base_model FROM experts')
            EXPERTS_CACHE = c.fetchall()
            conn.close()
    return EXPERTS_CACHE

def get_expert_response(expert, pergunta):
    """Faz requisição de API para um expert específico"""
    try:
        system_prompt = f"Você é {expert['name']}. {expert['description']}\n\n{expert['instructions']}"
        # Aqui você chama route_to_model(system_prompt, pergunta, expert['base_model'])
        # resposta = route_to_model(system_prompt, pergunta, expert['base_model'])
        return {
            'name': expert['name'],
            'resposta': 'resposta_aqui'  # Substitua por route_to_model
        }
    except Exception as e:
        return {
            'name': expert['name'],
            'resposta': None,
            'erro': str(e)
        }

def caos_otimizado(pergunta):
    """Endpoint /caos otimizado"""
    experts = load_experts_cache()
    
    if not experts:
        return {'success': False, 'error': 'Nenhum expert encontrado'}, 404
    
    respostas = []
    
    # Faz requisições em paralelo
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_expert_response, expert, pergunta): expert for expert in experts}
        
        for future in as_completed(futures):
            resposta = future.result()
            respostas.append(resposta)
    
    return {'success': True, 'respostas': respostas}, 200

print("Código de otimização criado!")
