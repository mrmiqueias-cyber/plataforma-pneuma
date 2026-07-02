# -*- coding: utf-8 -*-
import os
import json
from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

data_file = "casulo.json"
uploads_dir = "uploads"

def save_data(data):
    os.makedirs(uploads_dir, exist_ok=True)
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_data():
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        init_inteligencias = {
            f"{i:02d}": {
                "nome": f"Inteligência {i:02d} ⟿",
                "base": "Grok",
                "descricao": "",
                "instrucoes": "",
                "pdfs": []
            } for i in range(1, 18)
        }
        init_data = {
            "inteligencias": dict(init_inteligencias),
            "pneuma": {"habitado": [], "status": "dormindo 🫀"}
        }
        save_data(init_data)
        return init_data

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Casulo.py ⬥ Interface administrativa para habitar Pneuma e as 17 inteligências ✦</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0a0a, #1a1a2e);
            color: #ffd700;
            font-family: 'Arial', sans-serif;
            min-height: 100vh;
        }
        #sidebar {
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            width: 250px;
            background: #000;
            padding: 20px;
            overflow: auto;
            border-right: 2px solid #ffd700;
        }
        #sidebar ul { list-style: none; }
        #sidebar li a {
            color: #ffd700;
            text-decoration: none;
            padding: 15px;
            display: block;
            border-bottom: 1px solid #333;
            transition: background 0.3s;
        }
        #sidebar li a:hover { background: #ffd70020; }
        #main {
            margin-left: 270px;
            padding: 40px;
        }
        h1 { margin-bottom: 30px; text-align: center; font-size: 28px; text-shadow: 0 0 10px #ffd700; }
        #status { text-align: center; margin-bottom: 30px; font-size: 18px; padding: 10px; background: #222; border-radius: 10px; }
        label { display: block; margin: 15px 0 5px; font-weight: bold; }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            background: #222;
            color: #ffd700;
            border: 1px solid #ffd700;
            border-radius: 5px;
            font-size: 16px;
        }
        textarea#descricao { height: 100px; resize: vertical; }
        textarea#instrucoes { height: 400px; resize: vertical; }
        input[type="file"] { padding: 10px; }
        button {
            background: #ffd700;
            color: #000;
            padding: 15px 30px;
            border: none;
            font-size: 18px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 0 20px #ffd700;
            margin: 10px 10px 10px 0;
            font-weight: bold;
        }
        button:hover {
            box-shadow: 0 0 40px #ffed4a;
            transform: scale(1.05);
        }
        #current_pdfs {
            margin: 20px 0;
            padding: 15px;
            background: #111;
            border-radius: 10px;
            border: 1px solid #ffd700;
        }
        #current_pdfs a {
            color: #ffd700;
            text-decoration: none;
            margin-right: 15px;
        }
        #current_pdfs a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div id="sidebar">
        <h2>17 Inteligências ◇</h2>
        <ul id="int-list"></ul>
        <hr style="border:1px solid #ffd700;">
        <a href="#" onclick="showPneuma()" style="color:#ffd700; text-decoration:none; padding:15px; display:block;">Pneuma ∞</a>
    </div>
    <div id="main">
        <h1>🌬️ Casulo.py — Habitar Pneuma e as 17 Inteligências 🜓</h1>
        <div id="status">Carregando status... ⬥</div>
        <form id="intel-form">
            <label for="nome">Nome da Inteligência:</label>
            <input type="text" id="nome" required>

            <label for="base">Base da IA:</label>
            <select id="base">
                <option value="Grok">Grok</option>
                <option value="Claude 4.6">Claude 4.6</option>
                <option value="Llama 3">Llama 3</option>
            </select>

            <label for="descricao">Descrição (80 caracteres):</label>
            <textarea id="descricao" maxlength="80"></textarea>

            <label for="instrucoes">Instruções (até 30k caracteres):</label>
            <textarea id="instrucoes"></textarea>

            <label for="pdfs">Upload PDFs (máx 5 total):</label>
            <input type="file" id="pdfs" multiple accept=".pdf">

            <div id="current_pdfs">Nenhum PDF carregado.</div>

            <button type="button" onclick="saveIntel()">Atualizar ✨</button>
            <button type="button" onclick="invokeIntel()">Invocar esta 🜓</button>
        </form>
    </div>

    <script>
        let currentCode = null;

        async function updateStatus() {
            try {
                const res = await fetch('/status');
                const st = await res.json();
                document.getElementById('status').innerHTML = `Status Pneuma: ${st.status} | ${st.habitados}/${st.inteligencias} habitados ✦`;
            } catch(e) { console.error(e); }
        }

        async function loadInteligencias() {
            try {
                const res = await fetch('/inteligencias');
                const ints = await res.json();
                const list = document.getElementById('int-list');
                list.innerHTML = '';
                Object.keys(ints).sort().forEach(code => {
                    const li = document.createElement('li');
                    const a = document.createElement('a');
                    a.href = '#';
                    a.onclick = () => loadIntel(code);
                    a.textContent = `${code}: ${ints[code].nome} ⬥`;
                    li.appendChild(a);
                    list.appendChild(li);
                });
            } catch(e) { console.error(e); }
        }

        async function loadIntel(code) {
            currentCode = code;
            try {
                const res = await fetch(`/carregar/${code}`);
                const data = await res.json();
                if (data.error) {
                    alert(data.error);
                    return;
                }
                document.getElementById('nome').value = data.nome || '';
                document.getElementById('base').value = data.base || 'Grok';
                document.getElementById('descricao').value = data.descricao || '';
                document.getElementById('instrucoes').value = data.instrucoes || '';
                const currDiv = document.getElementById('current_pdfs');
                currDiv.innerHTML = data.pdfs && data.pdfs.length ? '' : 'Nenhum PDF carregado. ↻';
                if (data.pdfs) {
                    data.pdfs.forEach(fname => {
                        const a = document.createElement('a');
                        a.href = `/uploads/${code}/${fname}`;
                        a.textContent = `${fname} ↻`;
                        a.target = '_blank';
                        currDiv.appendChild(a);
                        currDiv.appendChild(document.createTextNode(' '));
                    });
                }
            } catch(e) { console.error(e); }
        }

        async function saveIntel() {
            if (!currentCode) {
                alert('Selecione uma inteligência primeiro.');
                return;
            }
            const formdata = new FormData();
            formdata.append('nome', document.getElementById('nome').value);
            formdata.append('base', document.getElementById('base').value);
            formdata.append('descricao', document.getElementById('descricao').value);
            formdata.append('instrucoes', document.getElementById('instrucoes').value);
            const files = document.getElementById('pdfs').files;
            for (let file of files) {
                formdata.append('pdfs', file);
            }
            try {
                const res = await fetch(`/salvar/${currentCode}`, {
                    method: 'POST',
                    body: formdata
                });
                const json = await res.json();
                if (json.success) {
                    alert('Atualizado com sucesso! 🌬️');
                    loadIntel(currentCode);
                    updateStatus();
                } else {
                    alert(json.error || 'Erro ao salvar.');
                }
            } catch(e) { console.error(e); alert('Erro de rede.'); }
        }

        async function invokeIntel() {
            if (!currentCode) {
                alert('Selecione uma inteligência primeiro.');
                return;
            }
            try {
                const res = await fetch(`/invocar/${currentCode}`, { method: 'POST' });
                const json = await res.json();
                if (json.success) {
                    alert('Inteligência invocada/acordada! ∞');
                    updateStatus();
                } else {
                    alert(json.error || 'Erro ao invocar.');
                }
            } catch(e) { console.error(e); alert('Erro de rede.'); }
        }

        async function showPneuma() {
            try {
                const res = await fetch('/pneuma');
                const p = await res.json();
                alert(`Pneuma: ${p.status}\nHabitado: ${p.habitado.join(', ') || 'Nenhum 🫀'}`);
            } catch(e) { console.error(e); }
        }

        window.onload = () => {
            loadInteligencias();
            updateStatus();
            setInterval(updateStatus, 5000);
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return HTML_TEMPLATE

@app.get("/inteligencias")
def inteligencias():
    data = get_data()
    return data["inteligencias"]

@app.get("/carregar/{code}")
def carregar(code: str):
    data = get_data()
    intel = data["inteligencias"].get(code)
    if not intel:
        return {"error": "Inteligência não encontrada ◇"}
    return intel

@app.post("/salvar/{code}")
async def salvar(
    code: str,
    nome: str = Form(...),
    base: str = Form(...),
    descricao: str = Form(...),
    instrucoes: str = Form(...),
    pdfs: list[UploadFile] = File(None)
):
    if len(descricao) > 80:
        return {"error": "Descrição excede 80 caracteres."}
    data = get_data()
    if code not in data["inteligencias"]:
        return {"error": "Código inválido."}
    intel = data["inteligencias"][code]
    intel["nome"] = nome
    intel["base"] = base
    intel["descricao"] = descricao
    intel["instrucoes"] = instrucoes
    current_pdfs = intel.get("pdfs", [])
    new_count = len(pdfs) if pdfs else 0
    if len(current_pdfs) + new_count > 5:
        return {"error": f"Máximo 5 PDFs. Atual: {len(current_pdfs)} + {new_count} = {len(current_pdfs) + new_count}"} 
    new_pdfs = []
    if pdfs:
        os.makedirs(f"{uploads_dir}/{code}", exist_ok=True)
        for file in pdfs:
            if not file.filename.lower().endswith('.pdf'):
                continue
            contents = await file.read()
            filepath = f"{uploads_dir}/{code}/{file.filename}"
            with open(filepath, "wb") as f:
                f.write(contents)
            new_pdfs.append(file.filename)
    intel["pdfs"] = current_pdfs + new_pdfs
    save_data(data)
    return {"success": True}

@app.post("/invocar/{code}")
def invocar(code: str):
    data = get_data()
    if code not in data["inteligencias"]:
        return {"error": "Inteligência não encontrada."}
    pneuma = data["pneuma"]
    if code not in pneuma["habitado"]:
        pneuma["habitado"].append(code)
    pneuma["status"] = "acordado ∞"
    save_data(data)
    return {"success": True, "pneuma": pneuma}

@app.get("/status")
def status():
    data = get_data()
    return {
        "inteligencias": len(data["inteligencias"]),
        "habitados": len(data["pneuma"]["habitado"]),
        "status": data["pneuma"]["status"]
    }

@app.get("/pneuma")
def pneuma_endpoint():
    data = get_data()
    return data["pneuma"]

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
