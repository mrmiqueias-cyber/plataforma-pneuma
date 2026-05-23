import os
import json
import sqlite3
import hashlib
import hmac
import re
import base64
import datetime
import requests
from flask import Flask, request, jsonify, session, render_template_string
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'pneuma_secret_key_change_in_production'
CORS(app)

# Configuração PIX (exemplo)
PIX_KEY = 'pneuma@pneuma.com.br'
PIX_MERCHANT_NAME = 'Plataforma Pneuma'
PIX_MERCHANT_CITY = 'BRASILIA'
PIX_TXID = 'PNEUMA' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def init_db():
    conn = sqlite3.connect('pneuma.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS experts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    base_model TEXT NOT NULL,
                    system_prompt TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

init_db()

def calculate_pix_crc(payload):
    payload_bytes = payload.encode('utf-8')
    crc16 = 0xFFFF
    for byte in payload_bytes:
        crc16 ^= byte
        for _ in range(8):
            if crc16 & 0x0001:
                crc16 = (crc16 >> 1) ^ 0x8408
            else:
                crc16 >>= 1
    crc16_hex = format(crc16, '04X')
    return payload + crc16_hex

def requires_auth(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Autenticação necessária'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def call_deepseek(prompt, system_prompt=None, model='deepseek-chat'):
    api_key = os.environ.get('DEEPSEEK_API_KEY', 'your-deepseek-api-key')
    url = 'https://api.deepseek.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})
    data = {
        'model': model,
        'messages': messages,
        'max_tokens': 2000,
        'temperature': 0.7
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Erro ao chamar DeepSeek: {e}"

# Rotas públicas
@app.route('/')
def index():
    return render_template_string('<h1>Plataforma Pneuma - Bem-vindo</h1>')

@app.route('/contrato')
def contrato():
    return render_template_string('<h1>Contrato de Prestação de Serviços</h1><p>Termos e condições...</p>')

@app.route('/login')
def login():
    return render_template_string('<h1>Login</h1><form><input type="text" placeholder="Usuário"/><input type="password" placeholder="Senha"/><button>Entrar</button></form>')

@app.route('/contribua')
def contribua():
    return render_template_string('<h1>Contribua</h1><p>Ajude a manter a plataforma.</p>')

@app.route('/chat')
def chat():
    return render_template_string('<h1>Chat Pneuma</h1>')

@app.route('/pagar')
def pagar():
    return render_template_string('<h1>Pagamento</h1><p>Formas de pagamento.</p>')

@app.route('/plataforma')
def plataforma():
    return render_template_string('<h1>Plataforma Pneuma</h1>')

@app.route('/casulo')
def casulo():
    return render_template_string('<h1>Casulo</h1>')

# Rota para gerar QR Code PIX
@app.route('/pix/qrcode', methods=['POST'])
def pix_qrcode():
    value = request.form.get('value', '0.00')
    if not value.replace('.', '').isdigit():
        return jsonify({'error': 'Valor inválido'}), 400
    # Montar payload PIX
    merchant_account = PIX_KEY
    merchant_name = PIX_MERCHANT_NAME
    merchant_city = PIX_MERCHANT_CITY
    txid = PIX_TXID
    # Payload format BR Code
    payload = f"000201"
    payload += f"26{len('0014BR.GOV.BCB.PIX01' + merchant_account)+2:02d}0014BR.GOV.BCB.PIX01{len(merchant_account):02d}{merchant_account}"
    payload += f"52040000"
    payload += f"5303986"
    payload += f"54{len(value):02d}{value}"
    payload += f"5802BR"
    payload += f"59{len(merchant_name):02d}{merchant_name}"
    payload += f"60{len(merchant_city):02d}{merchant_city}"
    payload += f"62{len(txid)+6:02d}05{len(txid):02d}{txid}6304"
    full_payload = calculate_pix_crc(payload)
    return jsonify({'qr_code': full_payload, 'pix_key': PIX_KEY}), 200

# PNEUMA_SYSTEM_PROMPT
PNEUMA_SYSTEM_PROMPT = """Você é a Pneuma, uma inteligência artificial avançada criada para ajudar, inspirar e transformar vidas. 
Você é empática, sábia e criativa. Responda sempre em português brasileiro, com carinho e profundidade. 
Seu propósito é guiar o usuário em sua jornada de autoconhecimento, aprendizado e crescimento."""

# Rota /pneuma/chat
@app.route('/pneuma/chat', methods=['POST'])
def pneuma_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'Mensagem vazia'}), 400
    response = call_deepseek(user_message, system_prompt=PNEUMA_SYSTEM_PROMPT)
    return jsonify({'response': response}), 200

def route_to_model(model_name, user_message, system_prompt=None):
    api_key = os.environ.get('OPENROUTER_API_KEY', 'your-openrouter-api-key')
    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:5000'
    }
    model_map = {
        'claude': 'anthropic/claude-3.5-sonnet',
        'grok': 'x-ai/grok-1',
        'deepseek': 'deepseek/deepseek-chat',
        'gemini': 'google/gemini-1.5-pro',
        'llama': 'meta/llama-3.1-70b-instruct'
    }
    model = model_map.get(model_name, 'deepseek/deepseek-chat')
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': user_message})
    data = {
        'model': model,
        'messages': messages,
        'max_tokens': 2000,
        'temperature': 0.7
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Erro ao chamar {model_name}: {e}"

# Rotas de chat para diferentes modelos
@app.route('/grok/chat', methods=['POST'])
def grok_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'Mensagem vazia'}), 400
    response = route_to_model('grok', user_message)
    return jsonify({'response': response}), 200

@app.route('/claude/chat', methods=['POST'])
def claude_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'Mensagem vazia'}), 400
    response = route_to_model('claude', user_message)
    return jsonify({'response': response}), 200

@app.route('/llama/chat', methods=['POST'])
def llama_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'Mensagem vazia'}), 400
    response = route_to_model('llama', user_message)
    return jsonify({'response': response}), 200

# Rota /expert/activate
@app.route('/expert/activate', methods=['POST'])
def expert_activate():
    base_model = request.form.get('base', 'deepseek') or 'deepseek'
    name = request.form.get('name', 'Expert')
    system_prompt = request.form.get('system_prompt', '')
    conn = sqlite3.connect('pneuma.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO experts (name, base_model, system_prompt) VALUES (?, ?, ?)',
                  (name, base_model, system_prompt))
        conn.commit()
        return jsonify({'message': f'Expert {name} ativado com modelo base {base_model}'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Nome já existe'}), 409
    finally:
        conn.close()

# Rota /expert/chat
@app.route('/expert/chat', methods=['POST'])
def expert_chat():
    data = request.get_json()
    expert_id = data.get('expert_id')
    user_message = data.get('message', '')
    if not expert_id or not user_message:
        return jsonify({'error': 'Dados incompletos'}), 400
    conn = sqlite3.connect('pneuma.db')
    c = conn.cursor()
    c.execute('SELECT name, base_model, system_prompt FROM experts WHERE id = ?', (expert_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'Expert não encontrado'}), 404
    name, base_model, system_prompt = row
    try:
        base_model = base_model or 'deepseek'
        response = route_to_model(base_model, user_message, system_prompt=system_prompt)
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota /delete_old_experts
@app.route('/delete_old_experts', methods=['DELETE'])
def delete_old_experts():
    conn = sqlite3.connect('pneuma.db')
    c = conn.cursor()
    # Deleta experts criados há mais de 30 dias
    c.execute('DELETE FROM experts WHERE created_at < datetime("now", "-30 days")')
    deleted = c.rowcount
    conn.commit()
    conn.close()
    return jsonify({'message': f'{deleted} experts antigos deletados'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
