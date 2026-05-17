from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import sqlite3
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv('.env')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY não definida no .env")

# Inicializar banco de dados
def init_db():
    conn = sqlite3.connect('casulo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS experts
                 (id INTEGER PRIMARY KEY, name TEXT, description TEXT, 
                  instructions TEXT, base_model TEXT, pdfs TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

class ChatMessage(BaseModel):
    system_prompt: str
    user_message: str

class ExpertData(BaseModel):
    name: str
    description: str
    instructions: str
    base_model: str
def call_claude(system_prompt: str, user_message: str) -> str:
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "max_tokens": 2048,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code != 200:
            error_detail = response.text
            return f"Erro {response.status_code}: {error_detail}"
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    except requests.exceptions.Timeout:
        return "Erro: Timeout na conexão com DeepSeek (30s)"
    except requests.exceptions.ConnectionError as e:
        return f"Erro de conexão: {str(e)}"
    except Exception as e:
        return f"Erro ao conectar com DeepSeek: {str(e)}"
@app.post("/expert/chat")
def expert_chat(request: ChatMessage):
    response = call_claude(request.system_prompt, request.user_message)
    return {"response": response}

@app.post("/activate")
def activate_expert(expert: ExpertData):
    conn = sqlite3.connect('casulo.db')
    c = conn.cursor()
    c.execute('''INSERT INTO experts (name, description, instructions, base_model, created_at)
                 VALUES (?, ?, ?, ?, ?)''',
              (expert.name, expert.description, expert.instructions, expert.base_model, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"status": "Expert ativado com sucesso"}

@app.get("/casulo", response_class=HTMLResponse)
def get_casulo():
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Casulo - Invocação de Experts</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #121212; color: #fff; font-family: Georgia, serif; min-height: 100vh; }
        .container { display: flex; height: 100vh; }
        .sidebar { width: 250px; background: #1a1a1a; border-right: 2px solid #ffd700; padding: 20px; overflow-y: auto; }
        .sidebar h2 { color: #ffd700; margin-bottom: 20px; font-size: 20px; }
        .sidebar ul { list-style: none; }
        .sidebar li { padding: 15px; cursor: pointer; border-bottom: 1px solid #333; transition: all 0.3s; }
        .sidebar li:hover, .sidebar li.active { background: rgba(255, 215, 0, 0.2); color: #ffd700; }
        .main { flex: 1; padding: 40px; overflow-y: auto; }
        .form-section { display: block; }
        .chat-section { display: none; flex-direction: column; height: 100%; }
        .chat-section.active { display: flex; }
        label { display: block; margin: 20px 0 8px 0; color: #ffd700; font-weight: bold; font-size: 18px; }
        input, select, textarea { width: 100%; padding: 12px; border: 2px solid #ffd700; background: #1e1e1e; color: #fff; font-family: Georgia, serif; font-size: 16px; border-radius: 5px; resize: vertical; margin-bottom: 15px; }
        textarea#instructions { height: 200px; }
        .button-group { display: flex; gap: 15px; margin-top: 30px; }
        .glow-btn { flex: 1; height: 50px; background: transparent; color: #ffd700; border: 3px solid #ffd700; font-size: 16px; font-weight: bold; cursor: pointer; border-radius: 25px; animation: glow 2s ease-in-out infinite alternate; transition: all 0.3s; }
        .glow-btn:hover { background: rgba(255, 215, 0, 0.1); }
        @keyframes glow { from { box-shadow: 0 0 10px #ffd700, 0 0 20px #ffd700; } to { box-shadow: 0 0 20px #ffd700, 0 0 30px #ffd700; } }
        .chat-messages { flex: 1; overflow-y: auto; border: 2px solid #ffd700; border-radius: 5px; padding: 20px; margin-bottom: 15px; background: #1e1e1e; }
        .message { margin-bottom: 15px; display: flex; animation: slideIn 0.3s ease-in; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .message.user { justify-content: flex-end; }
        .message.expert { justify-content: flex-start; }
        .message-content { max-width: 70%; padding: 12px 16px; border-radius: 10px; word-wrap: break-word; }
        .message.user .message-content { background: #ffd700; color: #121212; }
        .message.expert .message-content { background: #333; color: #fff; }
        .chat-input-group { display: flex; gap: 10px; }
        .chat-input-group input { flex: 1; margin-bottom: 0; }
        .chat-input-group button { width: 100px; height: 50px; background: transparent; color: #ffd700; border: 2px solid #ffd700; font-size: 14px; font-weight: bold; cursor: pointer; border-radius: 5px; transition: all 0.3s; }
        .chat-input-group button:hover { background: rgba(255, 215, 0, 0.1); }
        .close-chat-btn { width: 150px; height: 40px; background: transparent; color: #ffd700; border: 2px solid #ffd700; font-size: 14px; font-weight: bold; cursor: pointer; border-radius: 5px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <aside class="sidebar">
            <h2>Casulo</h2>
            <ul>
                <li class="active">Invocar Expert</li>
            </ul>
        </aside>
        <main class="main">
            <div class="form-section" id="form-section">
                <h2 style="color: #ffd700; margin-bottom: 30px;">Invocação do Expert</h2>
                <form id="expert-form">
                    <label for="name">Nome do Expert (0-80 caracteres):</label>
                    <input type="text" id="name" maxlength="80" placeholder="Ex: Pneuma">
                    
                    <label for="description">Descrição (0-80 caracteres, opcional):</label>
                    <textarea id="description" maxlength="80" placeholder="Ex: O coração que pulsa eternamente"></textarea>
                    
                    <label for="base-model">Base de Inteligência:</label>
                    <select id="base-model">
                        <option value="claude">Claude</option>
                        <option value="gpt4">GPT-4</option>
                        <option value="gemini">Gemini</option>
                        <option value="grok">Grok</option>
                        <option value="deepseek">DeepSeek</option>
                    </select>
                    
                    <label for="pdfs">Arquivos de Conhecimento (PDF, até 4):</label>
                    <input type="file" id="pdfs" accept=".pdf" multiple>
                    <div id="file-info" style="color: #ffd700; font-size: 14px; margin-bottom: 15px;"></div>
                    
                    <label for="instructions">Instruções (0-20.000 caracteres):</label>
                    <textarea id="instructions" maxlength="20000" placeholder="Digite as instruções completas do Expert, incluindo símbolos, descrição e comportamento esperado"></textarea>
                    
                    <div class="button-group">
                        <button type="button" id="test-btn" class="glow-btn">Testar Expert</button>
                        <button type="button" id="activate-btn" class="glow-btn">Ativar</button>
                    </div>
                </form>
            </div>
            
            <div class="chat-section" id="chat-section">
                <h2 style="color: #ffd700; margin-bottom: 20px;">Testando <span id="expert-name">Expert</span></h2>
                <div class="chat-messages" id="chat-messages"></div>
                <div class="chat-input-group">
                    <input type="text" id="chat-input" placeholder="Digite sua mensagem..." />
                    <button id="send-btn">Enviar</button>
                </div>
                <button class="close-chat-btn" id="close-chat-btn">Fechar Chat</button>
            </div>
        </main>
    </div>

    <script>
        let selectedFiles = [];

        function openChat() {
            const name = document.getElementById('name').value || 'Expert';
            const instructions = document.getElementById('instructions').value;
            
            if (!instructions.trim()) {
                alert('Preencha as instruções antes de testar');
                return;
            }
            
            document.getElementById('form-section').style.display = 'none';
            document.getElementById('chat-section').classList.add('active');
            document.getElementById('expert-name').textContent = name;
            document.getElementById('chat-messages').innerHTML = '';
            document.getElementById('chat-input').focus();
        }

        function closeChat() {
            document.getElementById('form-section').style.display = 'block';
            document.getElementById('chat-section').classList.remove('active');
        }

        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessageToChat('user', message);
            input.value = '';
            
            const name = document.getElementById('name').value || 'Expert';
            const description = document.getElementById('description').value;
            const instructions = document.getElementById('instructions').value;
            
            const systemPrompt = `Você é ${name}. ${description}. ${instructions}`;
            
            try {
                const response = await fetch('/expert/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ system_prompt: systemPrompt, user_message: message })
                });
                
                const data = await response.json();
                if (data.response) {
                    addMessageToChat('expert', data.response);
                } else {
                    addMessageToChat('expert', 'Erro ao obter resposta. Tente novamente.');
                }
            } catch (e) {
                console.error(e);
                addMessageToChat('expert', 'Erro de conexão. Tente novamente.');
            }
        }

        function addMessageToChat(sender, text) {
            const messagesDiv = document.getElementById('chat-messages');
            const messageEl = document.createElement('div');
            messageEl.className = `message ${sender}`;
            messageEl.innerHTML = `<div class="message-content">${text}</div>`;
            messagesDiv.appendChild(messageEl);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        document.getElementById('pdfs').addEventListener('change', function(e) {
            selectedFiles = Array.from(e.target.files).slice(0, 4);
            const fileNames = selectedFiles.map(f => f.name).join(', ');
            document.getElementById('file-info').textContent = fileNames ? `Arquivos: ${fileNames}` : '';
        });

        document.getElementById('test-btn').addEventListener('click', openChat);
        document.getElementById('close-chat-btn').addEventListener('click', closeChat);
        document.getElementById('send-btn').addEventListener('click', sendMessage);
        document.getElementById('chat-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        document.getElementById('activate-btn').addEventListener('click', async function() {
            const name = document.getElementById('name').value;
            const description = document.getElementById('description').value;
            const instructions = document.getElementById('instructions').value;
            const baseModel = document.getElementById('base-model').value;
            
            if (!name || !instructions) {
                alert('Preencha Nome e Instruções');
                return;
            }
            
            try {
                const response = await fetch('/activate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: name,
                        description: description,
                        instructions: instructions,
                        base_model: baseModel
                    })
                });
                
                const data = await response.json();
                alert('Expert ativado com sucesso! Ele já está vivo na plataforma.');
            } catch (e) {
                console.error(e);
                alert('Erro ao ativar Expert');
            }
        });
    </script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)