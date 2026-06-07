import sqlite3
import time
from flask import Response, request, stream_with_context

# Cache global dos experts
EXPERTS_CACHE = None

def load_experts_cache():
    global EXPERTS_CACHE
    if EXPERTS_CACHE is None:
        conn = sqlite3.connect('casulo.db', timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT id, name, description, instructions, base_model FROM experts WHERE is_fixed=1')
        EXPERTS_CACHE = c.fetchall()
        conn.close()
    return EXPERTS_CACHE

def caos_streaming(pergunta):
    """Endpoint caos com streaming SSE - respostas sequenciais com delay"""
    experts = load_experts_cache()
    
    if not experts:
        return {'success': False, 'error': 'Nenhum expert encontrado'}, 404
    
    def generate():
        for expert in experts:
            try:
                system_prompt = f"Você é {expert['name']}. {expert['description']}\n\n{expert['instructions']}"
                # Aqui você chama route_to_model(system_prompt, pergunta, expert['base_model'])
                resposta = route_to_model(system_prompt, pergunta, expert['base_model'])
            except Exception as e:
                resposta = f'Erro ao contatar {expert["name"]}: {str(e)}'
            
            # SSE Format
            yield f'data: {{"name": "{expert["name"]}", "resposta": "{resposta}"}}\n\n'
            
            # Delay entre respostas - 2 segundos para dar tempo de ler
            time.sleep(2.0)
    
    return Response(stream_with_context(generate()), mimetype='textevent-stream')
