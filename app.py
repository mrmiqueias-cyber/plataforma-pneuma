from fastapi import FastAPI, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import os

app = FastAPI()

data_file = "casulo.json"
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

def save_data(data):
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_data():
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        inteligencias = {}
        for i in range(1, 18):
            code = str(i)
            inteligencias[code] = {
                "name": f"Inteligência {i}",
                "base": "",
                "descricao": "",
                "instrucoes": "",
                "pdfs": [],
                "habitada": False
            }
        data = {
            "pneuma_status": "dormindo",
            "inteligencias": inteligencias
        }
        save_data(data)
        return data

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Casulo</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen p-8">
    <div class="max-w-7xl mx-auto flex">
        <div class="w-80 bg-gray-800 p-6 rounded-xl mr-8 shadow-2xl">
            <h2 class="text-2xl font-bold mb-6 text-blue-400">Inteligências</h2>
            <ul id="sidebar" class="space-y-3 mb-8">
                <!-- Populado por JS -->
            </ul>
            <div id="pneuma-status" class="p-4 bg-blue-900 rounded-lg text-center font-semibold">
                Pneuma: <span id="pneuma-text" class="text-blue-300">dormindo</span>
            </div>
        </div>
        <div class="flex-1 bg-gray-800 p-8 rounded-xl shadow-2xl">
            <div id="status" class="mb-8 p-6 bg-green-900 rounded-lg text-lg font-semibold">
                Total: <span id="total">-</span> | Habitadas: <span id="habitadas">-</span>
            </div>
            <form id="form" class="space-y-6">
                <input type="hidden" id="current-code">
                <div>
                    <label class="block text-sm font-bold mb-2 text-gray-300">Nome:</label>
                    <input type="text" id="name" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-sm font-bold mb-2 text-gray-300">Base:</label>
                    <textarea id="base" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-32 resize-vertical"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-bold mb-2 text-gray-300">Descrição (máx 80):</label>
                    <input type="text" id="descricao" maxlength="80" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <span id="desc-len" class="text-sm text-gray-500">0/80</span>
                </div>
                <div>
                    <label class="block text-sm font-bold mb-2 text-gray-300">Instruções:</label>
                    <textarea id="instrucoes" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-40 resize-vertical"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-bold mb-2 text-gray-300">PDFs (máx 5):</label>
                    <input type="file" id="pdf-files" multiple accept=".pdf" class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <div id="current-pdfs" class="mt-4 space-y-2">
                        <!-- PDFs atuais -->
                    </div>
                </div>
                <div class="flex space-x-4 pt-4">
                    <button type="button" id="salvar-btn" class="flex-1 bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-bold text-lg transition">Salvar</button>
                    <button type="button" id="invocar-btn" class="flex-1 bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-bold text-lg transition">Invocar</button>
                </div>
            </form>
            <div id="habitados-section" class="mt-12 p-6 bg-purple-900 rounded-lg">
                <h3 class="text-xl font-bold mb-4">Habitados:</h3>
                <ul id="habitados-list" class="space-y-1"></ul>
            </div>
        </div>
    </div>

<script>
    let inteligencias = {};

    async function loadAll() {
        try {
            const resp = await fetch('/inteligencias');
            inteligencias = await resp.json();
            updateSidebar();
            updateStatus();
        } catch (e) {
            console.error(e);
        }
        updatePneuma();
    }

    function updateSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.innerHTML = '';
        for (let code in inteligencias) {
            const li = document.createElement('li');
            const btn = document.createElement('button');
            btn.textContent = `${code}: ${inteligencias[code].name || 'Vazia'}`;
            btn.className = `w-full text-left p-3 rounded-lg transition ${inteligencias[code].habitada ? 'bg-green-500 hover:bg-green-600 text-white shadow-lg' : 'bg-gray-700 hover:bg-gray-600'}`;
            btn.onclick = () => loadInt(code);
            li.appendChild(btn);
            sidebar.appendChild(li);
        }
    }

    function updateStatus() {
        const total = Object.keys(inteligencias).length;
        const habitadas = Object.values(inteligencias).filter(i => i.habitada).length;
        document.getElementById('total').textContent = total;
        document.getElementById('habitadas').textContent = habitadas;
    }

    async function updatePneuma() {
        try {
            const resp = await fetch('/pneuma');
            const data = await resp.json();
            document.getElementById('pneuma-text').textContent = data.status;
            document.getElementById('pneuma-text').className = data.status === 'acordado' ? 'text-green-400 font-bold' : 'text-blue-300';
            const list = document.getElementById('habitados-list');
            list.innerHTML = '';
            if (data.habitados.length === 0) {
                const li = document.createElement('li');
                li.textContent = 'Nenhum';
                li.className = 'text-gray-400 italic';
                list.appendChild(li);
            } else {
                data.habitados.forEach(code => {
                    const li = document.createElement('li');
                    li.textContent = code;
                    li.className = 'bg-purple-700 p-2 rounded';
                    list.appendChild(li);
                });
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function loadInt(code) {
        document.getElementById('current-code').value = code;
        const int = inteligencias[code];
        document.getElementById('name').value = int.name || '';
        document.getElementById('base').value = int.base || '';
        document.getElementById('descricao').value = int.descricao || '';
        document.getElementById('instrucoes').value = int.instrucoes || '';
        const pdfsDiv = document.getElementById('current-pdfs');
        pdfsDiv.innerHTML = '';
        if (int.pdfs.length === 0) {
            pdfsDiv.innerHTML = '<p class="text-gray-500 text-sm">Nenhum PDF carregado.</p>';
        } else {
            int.pdfs.forEach(pdf => {
                const div = document.createElement('div');
                const a = document.createElement('a');
                a.href = `/uploads/${pdf}`;
                a.textContent = pdf;
                a.className = 'text-blue-400 hover:text-blue-300 underline';
                a.target = '_blank';
                div.appendChild(a);
                pdfsDiv.appendChild(div);
            });
        }
        updateDescLen();
    }

    function updateDescLen() {
        const desc = document.getElementById('descricao');
        document.getElementById('desc-len').textContent = `${desc.value.length}/80`;
    }

    document.getElementById('descricao').addEventListener('input', updateDescLen);

    document.getElementById('salvar-btn').onclick = async () => {
        const code = document.getElementById('current-code').value;
        const formData = new FormData();
        formData.append('name', document.getElementById('name').value);
        formData.append('base', document.getElementById('base').value);
        formData.append('descricao', document.getElementById('descricao').value);
        formData.append('instrucoes', document.getElementById('instrucoes').value);
        const files = document.getElementById('pdf-files').files;
        for (let i = 0; i < files.length; i++) {
            formData.append('pdfs', files[i]);
        }
        try {
            const resp = await fetch(`/salvar/${code}`, {
                method: 'POST',
                body: formData
            });
            const result = await resp.json();
            if (result.success) {
                alert('Dados salvos com sucesso!');
                const r = await fetch(`/carregar/${code}`);
                inteligencias[code] = await r.json();
                loadInt(code);
                updateSidebar();
            } else {
                alert('Erro: ' + (result.error || 'Falha ao salvar'));
            }
        } catch (e) {
            alert('Erro de rede: ' + e.message);
        }
    };

    document.getElementById('invocar-btn').onclick = async () => {
        const code = document.getElementById('current-code').value;
        try {
            const resp = await fetch(`/invocar/${code}`, { method: 'POST' });
            const result = await resp.json();
            if (result.success) {
                alert('Inteligência invocada! Pneuma acordado!');
                await loadAll();
                loadInt(code);
            } else {
                alert('Erro: ' + (result.error || 'Falha ao invocar'));
            }
        } catch (e) {
            alert('Erro de rede: ' + e.message);
        }
    };

    window.addEventListener('load', loadAll);
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTML_TEMPLATE

@app.get("/inteligencias")
async def get_inteligencias():
    data = get_data()
    return data["inteligencias"]

@app.get("/carregar/{code}")
async def carregar(code: str):
    data = get_data()
    if code in data["inteligencias"]:
        return data["inteligencias"][code]
    return {}

@app.post("/salvar/{code}")
async def salvar(
    code: str,
    name: str = Form(...),
    base: str = Form(""),
    descricao: str = Form(""),
    instrucoes: str = Form(""),
    pdfs: list[UploadFile] = File(None)
):
    if len(descricao) > 80:
        return {"error": "Descrição deve ter no máximo 80 caracteres"}

    data = get_data()
    if code not in data["inteligencias"]:
        return {"error": "Inteligência não encontrada"}

    int_data = data["inteligencias"][code]

    # Deletar PDFs antigos
    for pdf in int_data["pdfs"]:
        pdf_path = os.path.join(uploads_dir, pdf)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    new_pdfs = []
    if pdfs:
        if len(pdfs) > 5:
            return {"error": "Máximo de 5 PDFs"}
        for file in pdfs:
            if file.filename:
                filename = f"{code}_{file.filename}"
                file_path = os.path.join(uploads_dir, filename)
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                new_pdfs.append(filename)

    int_data["name"] = name
    int_data["base"] = base
    int_data["descricao"] = descricao
    int_data["instrucoes"] = instrucoes
    int_data["pdfs"] = new_pdfs

    save_data(data)
    return {"success": True}

@app.post("/invocar/{code}")
async def invocar(code: str):
    data = get_data()
    if code in data["inteligencias"]:
        data["inteligencias"][code]["habitada"] = True
        data["pneuma_status"] = "acordado"
        save_data(data)
        return {"success": True}
    return {"error": "Inteligência não encontrada"}

@app.get("/status")
async def status():
    data = get_data()
    inteligencias = data["inteligencias"]
    total = len(inteligencias)
    habitadas = sum(1 for v in inteligencias.values() if v["habitada"])
    return {
        "total": total,
        "habitadas": habitadas,
        "pneuma_status": data["pneuma_status"]
    }

@app.get("/pneuma")
async def pneuma_status():
    data = get_data()
    habitados = [code for code, int_data in data["inteligencias"].items() if int_data["habitada"]]
    return {
        "status": data["pneuma_status"],
        "habitados": habitados
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
