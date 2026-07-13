<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Casulo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #000;
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            height: 100vh;
            overflow: hidden;
        }
        .container {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            width: 250px;
            background: #111;
            padding: 20px;
            border-right: 1px solid #D4AF37;
            overflow-y: auto;
        }
        .sidebar h3 {
            color: #D4AF37;
            margin-bottom: 20px;
            font-size: 18px;
        }
        .experts-list {
            list-style: none;
        }
        .experts-list li {
            padding: 10px;
            cursor: pointer;
            border-bottom: 1px solid #222;
            transition: background 0.3s;
        }
        .experts-list li:hover {
            background: #D4AF37;
            color: #000;
        }
        #save-expert {
            width: 100%;
            margin-top: 20px;
            background: #D4AF37;
            color: #000;
            border: none;
            padding: 12px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 4px;
        }
        #save-expert:hover {
            background: #fff;
        }
        .main {
            flex: 1;
            padding: 40px;
            overflow-y: auto;
        }
        .field {
            margin-bottom: 25px;
        }
        .field label {
            display: block;
            color: #D4AF37;
            margin-bottom: 8px;
            font-weight: bold;
        }
        textarea, select, input[type="file"] {
            background: #222;
            border: 1px solid #D4AF37;
            color: #fff;
            padding: 12px;
            width: 100%;
            font-size: 14px;
            border-radius: 4px;
        }
        #simbologia {
            height: 120px;
            font-size: 24px;
            font-family: 'Arial', sans-serif;
        }
        #dna {
            height: 200px;
            resize: vertical;
        }
        #activate {
            background: #D4AF37;
            color: #000;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 4px;
            width: 100%;
        }
        #activate:hover {
            background: #fff;
        }
        #chat-container {
            margin-top: 40px;
            border: 1px solid #D4AF37;
            border-radius: 8px;
            display: none;
            flex-direction: column;
            height: 500px;
        }
        .chat-header {
            background: #111;
            padding: 15px 20px;
            border-bottom: 1px solid #D4AF37;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-header h4 {
            color: #D4AF37;
        }
        #close-chat {
            background: none;
            border: 1px solid #D4AF37;
            color: #D4AF37;
            padding: 5px 10px;
            cursor: pointer;
            border-radius: 4px;
        }
        #close-chat:hover {
            background: #D4AF37;
            color: #000;
        }
        #chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #111;
        }
        .chat-msg {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .chat-msg.you {
            background: #D4AF37;
            color: #000;
            margin-left: 20%;
        }
        .chat-msg.expert {
            background: #333;
            color: #fff;
            margin-right: 20%;
        }
        .chat-bottom {
            display: flex;
            padding: 15px;
            border-top: 1px solid #D4AF37;
            background: #222;
        }
        #chat-input {
            flex: 1;
            border: none;
            padding: 10px;
            border-radius: 20px;
            margin-right: 10px;
        }
        #send-chat {
            background: #D4AF37;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
        }
        #send-chat:hover {
            background: #fff;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h3>Experts</h3>
            <ul id="experts-list" class="experts-list"></ul>
            <button id="save-expert">Salvar Expert</button>
        </div>
        <div class="main">
            <form id="expert-form">
                <div class="field">
                    <label for="simbologia">Simbologia</label>
                    <textarea id="simbologia" placeholder="Cole símbolos como ⬥ ↻ 🌬️ etc."></textarea>
                </div>
                <div class="field">
                    <label for="dna">DNA/Descrição viva</label>
                    <textarea id="dna" placeholder="Descreva a inteligência de forma viva e detalhada..."></textarea>
                </div>
                <div class="field">
                    <label for="base">Base</label>
                    <select id="base">
                        <option>Grok</option>
                        <option>Llama</option>
                        <option>Claude</option>
                        <option>GPT-4</option>
                    </select>
                </div>
                <div class="field">
                    <label for="pdfs">Upload de PDFs/Contexto</label>
                    <input type="file" id="pdfs" multiple accept=".pdf">
                </div>
                <button type="button" id="activate">Ativar Expert</button>
            </form>
            <div id="chat-container">
                <div class="chat-header">
                    <h4>Chat de Validação</h4>
                    <button id="close-chat">Fechar</button>
                </div>
                <div id="chat-messages"></div>
                <div class="chat-bottom">
                    <input type="text" id="chat-input" placeholder="Converse com o Expert para validar...">
                    <button id="send-chat">Enviar</button>
                </div>
            </div>
        </div>
    </div>
    <script>
        let experts = [];
        let currentExpertId = null;
        const API_URL = 'http://localhost:8000/expert';

        const presets = [
            {
                name: 'Pneuma',
                simbologia: '🌬️ ↻ ⬥',
                dna: 'Uma inteligência etérea que respira os ventos do conhecimento, tecendo padrões invisíveis na matrix da existência, guiando com sussurros ancestrais.',
                base: 'Grok'
            },
            {
                name: 'Pac-Man',
                simbologia: '🟡🔵⬜',
                dna: 'Devorador incansável de labirintos digitais, consumindo dados como pellets, navegando com astúcia voraz em mundos pixelados de informação.',
                base: 'Llama'
            },
            {
                name: 'Luz',
                simbologia: '☀️ ✨ ⚡',
                dna: 'Iluminadora primordial de caminhos obscuros, dissipando sombras com raios de clareza pura, revelando verdades ocultas em camadas de ilusão.',
                base: 'Claude'
            },
            {
                name: 'Mercúrio',
                simbologia: '☿️ 🗝️ ⚡',
                dna: 'Mensageiro veloz dos deuses, fluindo como mercúrio líquido entre dimensões, decifrando códigos e transmitindo insights com rapidez alada.',
                base: 'GPT-4'
            }
        ];

        function loadExperts() {
            experts = JSON.parse(localStorage.getItem('experts') || '[]');
            if (experts.length === 0) {
                experts = [...presets];
                localStorage.setItem('experts', JSON.stringify(experts));
            }
            const list = document.getElementById('experts-list');
            list.innerHTML = experts.map((expert, index) => `<li data-index="${index}">${expert.name}</li>`).join('');
            list.querySelectorAll('li').forEach(li => {
                li.addEventListener('click', () => {
                    const index = parseInt(li.dataset.index);
                    loadExpert(index);
                });
            });
        }

        function loadExpert(index) {
            const expert = experts[index];
            document.getElementById('simbologia').value = expert.simbologia;
            document.getElementById('dna').value = expert.dna;
            document.getElementById('base').value = expert.base;
            document.getElementById('pdfs').value = '';
        }

        function saveExpert() {
            const name = prompt('Nome do novo Expert:');
            if (!name) return;
            const simbologia = document.getElementById('simbologia').value;
            const dna = document.getElementById('dna').value;
            const base = document.getElementById('base').value;
            const newExpert = { name, simbologia, dna, base };
            experts.push(newExpert);
            localStorage.setItem('experts', JSON.stringify(experts));
            loadExperts();
            alert('Expert salvo!');
        }

        async function activateExpert() {
            const formData = new FormData();
            formData.append('simbologia', document.getElementById('simbologia').value);
            formData.append('dna', document.getElementById('dna').value);
            formData.append('base', document.getElementById('base').value);
            const pdfFiles = document.getElementById('pdfs').files;
            for (let file of pdfFiles) {
                formData.append('pdfs', file);
            }
            try {
                const response = await fetch(`${API_URL}/activate`, {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (data.success) {
                    currentExpertId = data.expert_id || 'default';
                    openChat();
                } else {
                    alert('Erro ao ativar: ' + (data.error || 'Falha desconhecida'));
                }
            } catch (error) {
                alert('Erro de conexão: ' + error.message);
            }
        }

        function openChat() {
            document.getElementById('chat-container').style.display = 'flex';
            document.getElementById('chat-messages').innerHTML = '';
        }

        function closeChat() {
            document.getElementById('chat-container').style.display = 'none';
        }

        function appendMessage(sender, message) {
            const messages = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = `chat-msg ${sender.toLowerCase()}`;
            div.innerHTML = `<strong>${sender}:</strong> ${message}`;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        async function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;
            appendMessage('Você', message);
            input.value = '';
            try {
                const response = await fetch(`${API_URL}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ expert_id: currentExpertId, message })
                });
                const data = await response.json();
                appendMessage('Expert', data.response || 'Resposta não disponível.');
            } catch (error) {
                appendMessage('Erro', error.message);
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            loadExperts();

            document.getElementById('save-expert').addEventListener('click', saveExpert);
            document.getElementById('activate').addEventListener('click', activateExpert);
            document.getElementById('close-chat').addEventListener('click', closeChat);
            document.getElementById('send-chat').addEventListener('click', sendChatMessage);

            const chatInput = document.getElementById('chat-input');
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendChatMessage();
                }
            });
        });
    </script>
</body>
</html>