with open('instagram_automation.py', 'r', encoding='utf-8') as f:
    c = f.read()

dashboard_code = '''

# ============================================================================
# Metricas e Dashboard
# ============================================================================

def _salvar_metrica(expert: str, legenda: str, status: str) -> None:
    """Salva metrica de postagem no arquivo JSON."""
    import json
    from datetime import datetime
    metricas = []
    if os.path.exists(METRICAS_PATH):
        try:
            with open(METRICAS_PATH, "r", encoding="utf-8") as f:
                metricas = json.load(f)
        except (json.JSONDecodeError, IOError):
            metricas = []
    metricas.append({
        "expert": expert,
        "legenda": (legenda or "")[:200],
        "data_hora": datetime.now().isoformat(),
        "status": status,
    })
    metricas = metricas[-500:]
    try:
        with open(METRICAS_PATH, "w", encoding="utf-8") as f:
            json.dump(metricas, f, indent=2, ensure_ascii=False)
    except IOError as e:
        logger.warning("Nao foi possivel salvar metricas: %s", e)

@instagram_bp.route("/metricas", methods=["GET"])
def metricas_instagram():
    """Retorna o historico de postagens."""
    limite = request.args.get("limite", 50, type=int)
    expert = request.args.get("expert")
    metricas = []
    if os.path.exists(METRICAS_PATH):
        try:
            with open(METRICAS_PATH, "r", encoding="utf-8") as f:
                metricas = json.load(f)
        except (json.JSONDecodeError, IOError):
            metricas = []
    if expert:
        metricas = [m for m in metricas if m.get("expert") == expert]
    return jsonify({
        "total": len(metricas),
        "metricas": metricas[-limite:],
    })

@instagram_bp.route("/dashboard", methods=["GET"])
def dashboard_instagram():
    """Pagina visual do dashboard do Instagram da Pneuma."""
    metricas = []
    if os.path.exists(METRICAS_PATH):
        try:
            with open(METRICAS_PATH, "r", encoding="utf-8") as f:
                metricas = json.load(f)
        except (json.JSONDecodeError, IOError):
            metricas = []
    ultimas = metricas[-20:] if metricas else []
    s = "ativo" if scheduler.running else "inativo"
    ult_expert = str(_estado_automacao.get("ultimo_expert") or "---")
    ult_post = str(_estado_automacao.get("ultimo_post") or "Nenhum post ainda")
    prox_post = str(obter_proximo_post() or "---")
    total_posts = str(len(metricas))

    html = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Instagram da Pneuma</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
body{background:#0a0a0f;color:#e0e0e0;padding:20px;max-width:900px;margin:0 auto}
header{padding:12px 0 24px;border-bottom:1px solid #1a1a2e;margin-bottom:24px}
header h1{font-size:24px;color:#c0a0ff;margin-bottom:4px}
header p{font-size:13px;color:#666}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px}
.card{background:#12121a;border:1px solid #1e1e2e;border-radius:12px;padding:16px}
.card h3{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#888;margin-bottom:8px}
.card .valor{font-size:22px;font-weight:600}
.card .legenda{font-size:13px;color:#aaa;margin-top:6px}
.expert-tag{display:inline-block;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-top:6px}
.expert-Pneuma{background:rgba(192,160,255,.2);color:#c0a0ff}
.expert-Polis{background:rgba(74,222,128,.2);color:#4ade80}
.expert-Onirico{background:rgba(251,191,36,.2);color:#fbbf24}
section{margin-bottom:24px}
section h2{font-size:16px;margin-bottom:12px;color:#c0a0ff}
.tabela{width:100%;border-collapse:collapse;font-size:13px}
.tabela th{text-align:left;padding:8px 10px;color:#888;font-size:11px;text-transform:uppercase;border-bottom:1px solid #1e1e2e}
.tabela td{padding:8px 10px;border-bottom:1px solid #14141e}
.tabela tr:hover td{background:#18182a}
.status-badge{padding:2px 8px;border-radius:10px;font-size:11px}
.status-sucesso{background:rgba(74,222,128,.15);color:#4ade80}
.status-falha{background:rgba(248,113,113,.15);color:#f87171}
.agenda-item{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #14141e;font-size:13px}
.agenda-item:last-child{border:none}
.agenda-nome{color:#c0a0ff;font-weight:500}
.agenda-horario{color:#666}
.btn{display:inline-block;padding:8px 20px;border-radius:8px;border:none;font-size:13px;font-weight:600;cursor:pointer;transition:.2s;margin:4px}
.btn-primario{background:#c0a0ff;color:#0a0a0f}
select,textarea,input{background:#1a1a2e;color:#e0e0e0;border:1px solid #2e2e3e;border-radius:8px;padding:8px;font-size:13px;margin:4px;min-width:150px}
.manual-post{background:#12121a;border:1px solid #1e1e2e;border-radius:12px;padding:16px;margin-bottom:24px}
.manual-post h3{font-size:13px;margin-bottom:10px;color:#c0a0ff}
.toast{position:fixed;bottom:20px;right:20px;background:#1e1e2e;color:#e0e0e0;padding:12px 20px;border-radius:8px;font-size:13px;display:none;border:1px solid #2e2e3e}
</style>
</head>
<body>
<header>
<h1>Instagram da Pneuma</h1>
<p>Status da automacao social</p>
</header>
<div class="grid">
<div class="card"><h3>Scheduler</h3><div class="valor" style="color:""" + ("#4ade80" if scheduler.running else "#f87171") + """">""" + ("Ativo" if scheduler.running else "Inativo") + """</div></div>
<div class="card"><h3>Ultimo post</h3><div class="valor">""" + ult_expert + """</div><div class="legenda">""" + ult_post + """</div></div>
<div class="card"><h3>Proximo agendado</h3><div class="valor" style="font-size:14px">""" + prox_post + """</div></div>
<div class="card"><h3>Total de posts</h3><div class="valor">""" + total_posts + """</div></div>
</div>
<div class="manual-post">
<h3>Publicar manualmente</h3>
<form id="form-post">
<select name="expert">
<option value="Pneuma">Pneuma</option>
<option value="Polis">Polis</option>
<option value="Onirico">Onirico</option>
</select>
<textarea name="legenda" placeholder="Escreva a legenda do post..." rows="3"></textarea>
<button type="submit" class="btn btn-primario">Publicar agora</button>
</form>
</div>"""

    # Jobs agendados
    html += '<section><h2>Agendamentos</h2>'
    try:
        for job in scheduler.get_jobs():
            prox = job.next_run_time.strftime("%d/%m/%Y %H:%M") if job.next_run_time else "-"
            nome = job.args[0] if job.args else job.id
            html += '<div class="agenda-item"><span class="agenda-nome">' + nome + '</span><span class="agenda-horario">' + prox + '</span></div>'
    except:
        html += '<div class="agenda-item"><span class="agenda-nome">Scheduler nao iniciado</span></div>'
    html += '</section>'

    # Ultimas postagens
    if ultimas:
        html += '<section><h2>Ultimas postagens</h2><table class="tabela"><thead><tr><th>Expert</th><th>Data</th><th>Status</th><th>Legenda</th></tr></thead><tbody>'
        for m in reversed(ultimas):
            sc = "status-sucesso" if m.get("status") == "sucesso" else "status-falha"
            et = "expert-" + (m.get("expert") or "")
            html += '<tr><td><span class="expert-tag ' + et + '">' + (m.get("expert") or "") + '</span></td><td style="color:#888;font-size:12px">' + (m.get("data_hora","")[:16]) + '</td><td><span class="status-badge ' + sc + '">' + (m.get("status") or "") + '</span></td><td style="color:#aaa;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + ((m.get("legenda") or "")[:80]) + '</td></tr>'
        html += '</tbody></table></section>'

    html += '''<div id="toast" class="toast"></div>
<script>
document.getElementById("form-post").addEventListener("submit",async function(e){
e.preventDefault();
const btn=this.querySelector("button[type=submit]");
btn.textContent="Publicando...";
btn.disabled=true;
const fd=new FormData(this);
try{
const resp=await fetch("/instagram/postar",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({expert:fd.get("expert"),legenda:fd.get("legenda")})});
const data=await resp.json();
const t=document.getElementById("toast");
t.style.display="block";
t.style.background=data.sucesso?"rgba(74,222,128,.2)":"rgba(248,113,113,.2)";
t.style.color=data.sucesso?"#4ade80":"#f87171";
t.textContent=data.sucesso?"Post publicado!":"Erro: "+data.erro;
setTimeout(function(){t.style.display="none"},4000);
if(data.sucesso) setTimeout(function(){location.reload()},2000);
}catch(e){
const t=document.getElementById("toast");
t.style.display="block";
t.style.background="rgba(248,113,113,.2)";
t.style.color="#f87171";
t.textContent="Erro de conexao";
setTimeout(function(){t.style.display="none"},4000);
}finally{btn.textContent="Publicar agora";btn.disabled=false}
});
</script>
</body></html>'''
    return html
'''

insert_pos = c.find('\ndef init_app(app):')
if insert_pos > 0:
    c = c[:insert_pos] + dashboard_code + c[insert_pos:]
    with open('instagram_automation.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Dashboard adicionado com sucesso!")
else:
    print("ERRO: nao encontrei 'def init_app(app)' no arquivo")