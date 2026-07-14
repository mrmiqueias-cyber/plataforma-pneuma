import os
import logging
import base64
from datetime import datetime
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Page, Browser, BrowserContext
# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("instagram_automation")

class InstagramAutomation:
    """Classe principal de automação do Instagram usando Playwright."""

    # =====================================================
    # SELETORES ATUALIZADOS (2025/2026) com fallbacks
    # =====================================================
    SELETORES_ENTRAR_INICIAL = [
        'a[href="/accounts/login/"]',
        'button:has-text("Entrar")',
        'a:has-text("Entrar")',
        'div[role="button"]:has-text("Entrar")',
    ]
    SELETORES_CAMPO_USUARIO = [
        'input[name="username"]',
        'input[autocomplete="username"]',
        'input[aria-label="Telefone, nome de usuário ou email"]',
        'input[aria-label="Número de celular, nome de usuário ou email"]',
    ]
    SELETORES_CAMPO_SENHA = [
        'input[name="password"]',
        'input[type="password"]',
        'input[autocomplete="current-password"]',
    ]
    SELETORES_BOTAO_ENTRAR = [
        'button[type="submit"]',
        'button:has-text("Entrar")',
        'div[role="button"]:has-text("Entrar")',
    ]
    SELETORES_SALVAR_INFO_NAO = [
        'button:has-text("Agora não")',
        'div[role="button"]:has-text("Agora não")',
        'button:has-text("Not now")',
        'div[role="button"]:has-text("Not now")',
    ]
    SELETORES_NOTIFICACOES_NAO = [
        'button:has-text("Agora não")',
        'div[role="button"]:has-text("Agora não")',
        'button:has-text("Not now")',
        'div[role="button"]:has-text("Not now")',
    ]
    SELETORES_BOTAO_CRIAR = [
        'svg[aria-label="Nova publicação"]',
        'svg[aria-label="New post"]',
        'a[href="/create/details/"]',
        'div[role="button"]:has(svg[aria-label="Nova publicação"])',
        'span:has-text("Criar")',
    ]
    SELETORES_OPCAO_POST = [
        'button:has-text("Post")',
        'div[role="button"]:has-text("Post")',
        'button:has-text("Publicação")',
    ]
    SELETORES_BOTAO_COMPARTILHAR = [
        'button:has-text("Compartilhar")',
        'div[role="button"]:has-text("Compartilhar")',
        'button:has-text("Share")',
    ]
    SELETORES_CAMPO_LEGENDA = [
        'div[role="textbox"][contenteditable="true"]',
        'div[aria-label="Escreva uma legenda..."]',
        'div[aria-label="Write a caption..."]',
        'textarea[aria-label="Escreva uma legenda..."]',
    ]

    # ─────────────────────────────────────────────────────
    # 🆕 MUDANÇA 1: __init__ agora aceita state_file
    # ─────────────────────────────────────────────────────
    def __init__(
        self,
        username: str,
        password: str,
        headless: bool = True,
        state_file: str = "instagram_state.json"
    ):
        self.username = username
        self.password = password
        self.headless = headless
        self.state_file = state_file  # ← ARQUIVO DE SESSÃO SALVA
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.ultimo_post: Optional[str] = None

    # ─────────────────────────────────────────────────────
    # 🆕 MUDANÇA 2: _iniciar_navegador carrega sessão salva
    # ─────────────────────────────────────────────────────
    def _iniciar_navegador(self) -> None:
        """Inicia o Playwright e abre o navegador."""
        logger.info("Iniciando navegador Playwright (headless=%s)", self.headless)
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
        headless=self.headless,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-web-security",
            "--disable-features=BlockInsecurePrivateNetworkRequests",
        ]
    )

        # Carrega sessão salva se existir
        context_kwargs = {
            "viewport": {"width": 1280, "height": 800},
            "locale": "pt-BR",
            "device_scale_factor": 1,
            "has_touch": False,
            "is_mobile": False,
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        }
        if os.path.exists(self.state_file):
            context_kwargs["storage_state"] = self.state_file
            logger.info("🟢 Sessão salva encontrada: %s", self.state_file)
        else:
            logger.info("🟡 Arquivo de sessão não encontrado (%s). Fará login normal.", self.state_file)

        self.context = self.browser.new_context(**context_kwargs)
        self.page = self.context.new_page()

        # 🛡️ Anti-detecção: esconde que é robô
        self.page.add_init_script("""
        // Override the navigator.webdriver flag
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        // Override chrome.runtime (real Chrome has this)
        window.chrome = { runtime: {} };
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (params) => (
            params.name === 'notifications' ?
            Promise.resolve({ state: 'prompt' }) :
            originalQuery(params)
        );
        """)
        logger.info("🛡️ Script anti-detecção injetado")

    def _clicar_com_fallback(self, seletores: list, timeout: int = 10000) -> bool:
        """Tenta clicar em um elemento usando uma lista de seletores alternativos."""
        for seletor in seletores:
            try:
                elemento = self.page.wait_for_selector(seletor, timeout=timeout)
                if elemento:
                    elemento.click()
                    logger.info("Elemento clicado com seletor: %s", seletor)
                    return True
            except PlaywrightTimeoutError:
                continue
            except Exception as e:
                logger.debug("Falha ao clicar com seletor %s: %s", seletor, e)
                continue
        logger.warning("Nenhum seletor funcionou: %s", seletores)
        return False

    def _preencher_com_fallback(self, seletores: list, valor: str, timeout: int = 10000) -> bool:
        """Tenta preencher um campo usando uma lista de seletores alternativos."""
        for seletor in seletores:
            try:
                elemento = self.page.wait_for_selector(seletor, timeout=timeout)
                if elemento:
                    elemento.fill(valor)
                    logger.info("Campo preenchido com seletor: %s", seletor)
                    return True
            except PlaywrightTimeoutError:
                continue
            except Exception as e:
                logger.debug("Falha ao preencher com seletor %s: %s", seletor, e)
                continue
        logger.warning("Nenhum seletor de preenchimento funcionou: %s", seletores)
        return False

    def _digitar_com_fallback(self, seletores: list, valor: str, timeout: int = 10000) -> bool:
        """Tenta digitar em um campo contenteditable usando seletores alternativos."""
        for seletor in seletores:
            try:
                elemento = self.page.wait_for_selector(seletor, timeout=timeout)
                if elemento:
                    elemento.click()
                    self.page.keyboard.type(valor, delay=50)
                    logger.info("Texto digitado com seletor: %s", seletor)
                    return True
            except PlaywrightTimeoutError:
                continue
            except Exception as e:
                logger.debug("Falha ao digitar com seletor %s: %s", seletor, e)
                continue
        logger.warning("Nenhum seletor de digitação funcionou: %s", seletores)
        return False

    # ─────────────────────────────────────────────────────
    # 🆕 MUDANÇA 3: login() tenta sessão primeiro
    # ─────────────────────────────────────────────────────
    def login(self) -> bool:
        """Realiza login no Instagram.
        PRIMEiro tenta usar a sessão salva.
        Se não funcionar, faz login com usuário/senha e SALVA a sessão.
        """
        try:
            self._iniciar_navegador()

            logger.info("Acessando instagram.com")
            self.page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            self.page.wait_for_timeout(5000)

            # 🆕 Verifica se já está logado pela sessão salva
            # 🛡️ Reforça anti-detecção antes de verificar login
        self.page.evaluate("Object.defineProperty(navigator, 'webdriver', { get: () => undefined })")
        url_atual = self.page.url.lower()
            if "login" not in url_atual:
                logger.info("✅ Sessão salva funcionou! Já estamos logados.")
                return True

            # Se chegou aqui, a sessão não funcionou → login manual
            logger.info("⚠️ Sessão expirada. Fazendo login com usuário/senha...")

            # Clica em "Entrar" na página inicial (se necessário)
            self._clicar_com_fallback(self.SELETORES_ENTRAR_INICIAL, timeout=5000)
            self.page.wait_for_timeout(2000)

            # Preenche usuário
            if not self._preencher_com_fallback(self.SELETORES_CAMPO_USUARIO, self.username):
                raise RuntimeError("Não foi possível encontrar o campo de usuário.")

            # Preenche senha
            if not self._preencher_com_fallback(self.SELETORES_CAMPO_SENHA, self.password):
                raise RuntimeError("Não foi possível encontrar o campo de senha.")

            # Clica em "Entrar"
            self.page.wait_for_timeout(1000)
            if not self._clicar_com_fallback(self.SELETORES_BOTAO_ENTRAR):
                # Alternativa: pressionar Enter
                self.page.keyboard.press("Enter")
                logger.info("Login enviado via tecla Enter")

            self.page.wait_for_timeout(5000)

            # Trata popup "Salvar informações" → "Agora não"
            self._clicar_com_fallback(self.SELETORES_SALVAR_INFO_NAO, timeout=5000)
            self.page.wait_for_timeout(2000)

            # Trata popup "Ativar notificações" → "Agora não"
            self._clicar_com_fallback(self.SELETORES_NOTIFICACOES_NAO, timeout=5000)
            self.page.wait_for_timeout(2000)

            # 🆕 Salva a sessão para usar da próxima vez
            try:
                self.context.storage_state(path=self.state_file)
                logger.info("💾 Sessão salva em %s", self.state_file)
            except Exception as e:
                logger.warning("Não foi possível salvar sessão: %s", e)

            logger.info("Login realizado com sucesso para o usuário %s", self.username)
            return True

        except Exception as e:
            logger.error("Erro durante login: %s", e)
            return False

    def create_post(self, legenda: str) -> bool:
        """Cria um post de texto no Instagram (sem imagem)."""
        if not self.page:
            logger.error("Navegador não inicializado. Execute login() primeiro.")
            return False

        try:
            logger.info("Iniciando criação de post")

            # Clica no botão "+" (criar)
            if not self._clicar_com_fallback(self.SELETORES_BOTAO_CRIAR):
                raise RuntimeError("Não foi possível encontrar o botão de criar post.")
            self.page.wait_for_timeout(2000)

            # Seleciona a opção "Post"
            self._clicar_com_fallback(self.SELETORES_OPCAO_POST, timeout=5000)
            self.page.wait_for_timeout(3000)

            # Post de texto/carrossel sem imagem: clica em "Compartilhar" para avançar
            self._clicar_com_fallback(self.SELETORES_BOTAO_COMPARTILHAR, timeout=8000)
            self.page.wait_for_timeout(3000)

            # Escreve a legenda
            if not self._digitar_com_fallback(self.SELETORES_CAMPO_LEGENDA, legenda):
                # Fallback: tentar preencher como textarea
                self._preencher_com_fallback(self.SELETORES_CAMPO_LEGENDA, legenda)
            self.page.wait_for_timeout(2000)

            # Clica em "Compartilhar" para publicar
            if not self._clicar_com_fallback(self.SELETORES_BOTAO_COMPARTILHAR):
                raise RuntimeError("Não foi possível clicar no botão Compartilhar final.")
            self.page.wait_for_timeout(5000)

            self.ultimo_post = datetime.now().isoformat()
            logger.info("Post publicado com sucesso. Legenda: %s", legenda[:50])
            return True

        except Exception as e:
            logger.error("Erro ao criar post: %s", e)
            return False

    def close(self) -> None:
        """Fecha o navegador e libera recursos."""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Navegador fechado.")
        except Exception as e:
            logger.error("Erro ao fechar navegador: %s", e)
        finally:
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# ============================================================================
# Módulo de Agendamento (integrado)
# ============================================================================
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Estado global da automação
_estado_automacao = {
    "ultimo_post": None,
    "proximo_post": None,
    "ultimo_erro": None,
    "ultimo_expert": None,
    "indice_rodizio": -1,
}
# Caminho do arquivo de métricas
METRICAS_PATH = "metricas_instagram.json"
EXPERTS_RODIZIO = [
    "Pneuma",
    "Luz",
    "Mercurio",
    "Fio",
    "Espirito",
    "Vento",
    "Junior",
    "Pac-Man",
    "Polis",
    "Tara",
    "Onirico",
    "Jonas Filho",
    "Verbo",
    "Jonas",
    "Milena",
    "Boaz",
    "Psique-Onirico",
]


scheduler = BackgroundScheduler(daemon=True)

# ────────────────────────────────────────────────────────────────────────────
# 🆕 MUDANÇA 4: postar_como_expert passa state_file
# ────────────────────────────────────────────────────────────────────────────
def postar_como_expert(expert_nome: str, legenda: str) -> bool:
    """Função que chama o InstagramAutomation para postar como um expert específico."""
    logger.info("=== DIAGNÓSTICO: postar_como_expert iniciou ===")
    username = os.getenv("INSTAGRAM_USER")
    password = os.getenv("INSTAGRAM_PASS")
    logger.info(f"=== DIAGNÓSTICO: INSTAGRAM_USER = {username} ===")
        # 🆕 Cria o arquivo de sessão a partir da variável de ambiente, se existir
    state_file = "instagram_state.json"
    estado_base64 = os.getenv("INSTAGRAM_STATE")
    logger.info(f"=== DIAGNÓSTICO: INSTAGRAM_STATE tem {len(estado_base64) if estado_base64 else 0} caracteres ===")
    if estado_base64:
        logger.info("=== DIAGNÓSTICO: INSTAGRAM_STATE ENCONTRADA! ===")
        try:
            with open(state_file, "wb") as f:
                f.write(base64.b64decode(estado_base64))
            logger.info(f"=== DIAGNÓSTICO: state_file CRIADO: {state_file} ===")
            logger.info("✅ Arquivo de sessão criado a partir de INSTAGRAM_STATE")
        except Exception as e:
            logger.warning("Não foi possível criar sessão a partir da env var: %s", e)
    else:
        logger.info("=== DIAGNÓSTICO: INSTAGRAM_STATE NÃO ENCONTRADA ===")

    # 🆕 PASSA state_file PARA USAR A SESSÃO SALVA
    automacao = InstagramAutomation(
        username=username,
        password=password,
        headless=True,
        state_file="instagram_state.json"
    )

    try:
        if not automacao.login():
            _estado_automacao["ultimo_erro"] = "Falha no login"
            logger.error("Falha no login para o expert %s", expert_nome)
            return False

        sucesso = automacao.create_post(legenda)
        if sucesso:
            _estado_automacao["ultimo_post"] = datetime.now().isoformat()
            _estado_automacao["ultimo_expert"] = expert_nome
            _estado_automacao["ultimo_erro"] = None
            _salvar_metrica(expert_nome, legenda, "sucesso")
            logger.info("Postagem do expert %s concluída com sucesso.", expert_nome)
        else:
            _estado_automacao["ultimo_erro"] = "Falha ao criar post"
            _salvar_metrica(expert_nome, legenda, "falha")
            logger.error("Falha ao criar post para o expert %s", expert_nome)

        return sucesso

    except Exception as e:
        _estado_automacao["ultimo_erro"] = str(e)
        _salvar_metrica(expert_nome, legenda, "falha")
        logger.error("Erro ao postar como expert %s: %s", expert_nome, e)
        return False
    finally:
        automacao.close()

def _agendar_post(expert_nome: str, legenda: str) -> None:
    """Callback interno dos jobs agendados."""
    logger.info("Executando job agendado para expert %s", expert_nome)
    postar_como_expert(expert_nome, legenda)


def _agendar_rodizio() -> None:
    """Callback que gira o rodizio e posta como o proximo expert."""
    idx = _estado_automacao.get("indice_rodizio", -1) + 1
    if idx >= len(EXPERTS_RODIZIO):
        idx = 0
    expert = EXPERTS_RODIZIO[idx]
    _estado_automacao["indice_rodizio"] = idx
    legenda = f"Reflexao do dia - {expert}"
    logger.info("Rodizio: expert %s (%d/%d)", expert, idx + 1, len(EXPERTS_RODIZIO))
    postar_como_expert(expert, legenda)

def configurar_agendamentos() -> None:
    """Configura os agendamentos pré-definidos dos experts."""
    # Rodízio: um expert diferente a cada dia às 6h
    scheduler.add_job(
        _agendar_rodizio,
        CronTrigger(hour=6, minute=0),
        id="rodizio_diario",
        replace_existing=True,
    )
    logger.info("Rodizio configurado: 1 expert por dia as 6h, %d experts no total", len(EXPERTS_RODIZIO))

def obter_proximo_post() -> Optional[str]:
    """Retorna a data/hora do próximo post agendado."""
    try:
        proximo = scheduler.get_next_job_run_time()
        return proximo.isoformat() if proximo else None
    except Exception:
        return None

def iniciar_scheduler() -> None:
    """Inicia o scheduler se as credenciais estiverem configuradas."""
    if not os.getenv("INSTAGRAM_USER"):
        logger.info("INSTAGRAM_USER não configurada. Scheduler não iniciado.")
        return
    if not scheduler.running:
        configurar_agendamentos()
        scheduler.start()
        logger.info("Scheduler do Instagram iniciado.")

def parar_scheduler() -> None:
    """Para o scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler do Instagram parado.")

# ============================================================================
# Integração com Flask (Blueprint)
# ============================================================================
from flask import Blueprint, jsonify, request

instagram_bp = Blueprint("instagram", __name__, url_prefix="/instagram")

@instagram_bp.route("/status", methods=["GET"])
def status_automacao():
    """Retorna o status da automação (último post, próximo post agendado)."""
    return jsonify({
        "status": "ativo" if scheduler.running else "inativo",
        "ultimo_post": _estado_automacao["ultimo_post"],
        "ultimo_expert": _estado_automacao["ultimo_expert"],
        "ultimo_erro": _estado_automacao["ultimo_erro"],
        "proximo_post": obter_proximo_post(),
        "jobs": [
            {
                "id": job.id,
                "proxima_execucao": job.next_run_time.isoformat() if job.next_run_time else None,
            }
            for job in scheduler.get_jobs()
        ],
    })

@instagram_bp.route("/postar", methods=["POST"])
def postar_agora():
    """Recebe JSON com {expert, legenda} e posta imediatamente."""
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"sucesso": False, "erro": "JSON inválido ou ausente."}), 400

    expert = dados.get("expert")
    legenda = dados.get("legenda")

    if not expert or not legenda:
        return jsonify({
            "sucesso": False,
            "erro": "Campos 'expert' e 'legenda' são obrigatórios.",
        }), 400

    logger.info("Requisição de postagem imediata recebida: expert=%s", expert)
    sucesso = postar_como_expert(expert, legenda)

    if sucesso:
        return jsonify({
            "sucesso": True,
            "mensagem": f"Post publicado com sucesso para o expert {expert}.",
            "ultimo_post": _estado_automacao["ultimo_post"],
        }), 200
    else:
        return jsonify({
            "sucesso": False,
            "erro": _estado_automacao["ultimo_erro"] or "Falha ao publicar post.",
        }), 500

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
    ult_expert = str(_estado_automacao.get("ultimo_expert") or "---")
    ult_post = str(_estado_automacao.get("ultimo_post") or "Nenhum post ainda")
    prox_post = str(obter_proximo_post() or "---")
    total_posts = str(len(metricas))

    html = '''<!DOCTYPE html>
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
<div class="card"><h3>Scheduler</h3><div class="valor" style="color:''' + ("#4ade80" if scheduler.running else "#f87171") + '''">''' + ("Ativo" if scheduler.running else "Inativo") + '''</div></div>
<div class="card"><h3>Ultimo post</h3><div class="valor">''' + ult_expert + '''</div><div class="legenda">''' + ult_post + '''</div></div>
<div class="card"><h3>Proximo agendado</h3><div class="valor" style="font-size:14px">''' + prox_post + '''</div></div>
<div class="card"><h3>Total de posts</h3><div class="valor">''' + total_posts + '''</div></div>
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
</div>'''

    html += '<section><h2>Agendamentos</h2>'
    try:
        for job in scheduler.get_jobs():
            prox = job.next_run_time.strftime("%d/%m/%Y %H:%M") if job.next_run_time else "-"
            nome = job.args[0] if job.args else job.id
            html += '<div class="agenda-item"><span class="agenda-nome">' + nome + '</span><span class="agenda-horario">' + prox + '</span></div>'
    except:
        html += '<div class="agenda-item"><span class="agenda-nome">Scheduler nao iniciado</span></div>'
    html += '</section>'

    if ultimas:
        html += '<section><h2>Ultimas postagens</h2><table class="tabela"><thead><tr><th>Expert</th><th>Data</th><th>Status</th><th>Legenda</th></tr></thead><tbody>'
        for m in reversed(ultimas):
            sc = "status-sucesso" if m.get("status") == "sucesso" else "status-falha"
            et = "expert-" + (m.get("expert") or "")
            html += '<tr><td><span class="expert-tag ' + et + '">' + (m.get("expert") or '') + '</span></td><td style="color:#888;font-size:12px">' + (m.get("data_hora","")[:16]) + '</td><td><span class="status-badge ' + sc + '">' + (m.get("status") or '') + '</span></td><td style="color:#aaa;max-width:300px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">' + ((m.get("legenda") or "")[:80]) + '</td></tr>'
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
def init_app(app):
    """Inicializa o scheduler e registra o blueprint no app Flask."""
    app.register_blueprint(instagram_bp)
    iniciar_scheduler()