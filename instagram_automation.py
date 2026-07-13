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
        self.browser = self.playwright.chromium.launch(headless=self.headless)

        # Carrega sessão salva se existir
        context_kwargs = {
            "viewport": {"width": 1280, "height": 800},
            "locale": "pt-BR",
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
}

scheduler = BackgroundScheduler(daemon=True)

# ────────────────────────────────────────────────────────────────────────────
# 🆕 MUDANÇA 4: postar_como_expert passa state_file
# ────────────────────────────────────────────────────────────────────────────
def postar_como_expert(expert_nome: str, legenda: str) -> bool:
    """Função que chama o InstagramAutomation para postar como um expert específico."""
    username = os.getenv("INSTAGRAM_USER")
    password = os.getenv("INSTAGRAM_PASS")
    # 🆕 Cria o arquivo de sessão a partir da variável de ambiente, se existir
    state_file = "instagram_state.json"
    estado_base64 = os.getenv("INSTAGRAM_STATE")
    if estado_base64:
        try:
            with open(state_file, "wb") as f:
                f.write(base64.b64decode(estado_base64))
            logger.info("✅ Arquivo de sessão criado a partir de INSTAGRAM_STATE")
        except Exception as e:
            logger.warning("Não foi possível criar sessão a partir da env var: %s", e)

    if not username or not password:
        logger.error("Credenciais do Instagram não configuradas nas variáveis de ambiente.")
        _estado_automacao["ultimo_erro"] = "Credenciais não configuradas"
        return False

    logger.info("Iniciando postagem para o expert %s", expert_nome)

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
            logger.info("Postagem do expert %s concluída com sucesso.", expert_nome)
        else:
            _estado_automacao["ultimo_erro"] = "Falha ao criar post"
            logger.error("Falha ao criar post para o expert %s", expert_nome)

        return sucesso

    except Exception as e:
        _estado_automacao["ultimo_erro"] = str(e)
        logger.error("Erro ao postar como expert %s: %s", expert_nome, e)
        return False
    finally:
        automacao.close()

def _agendar_post(expert_nome: str, legenda: str) -> None:
    """Callback interno dos jobs agendados."""
    logger.info("Executando job agendado para expert %s", expert_nome)
    postar_como_expert(expert_nome, legenda)

def configurar_agendamentos() -> None:
    """Configura os agendamentos pré-definidos dos experts."""
    # Polis: terça e quinta às 8h
    scheduler.add_job(
        _agendar_post,
        CronTrigger(day_of_week="tue,thu", hour=8, minute=0),
        args=["Polis", "Reflexão do dia - Polis"],
        id="polis_terca_quinta",
        replace_existing=True,
    )
    # Onírico: quarta e sexta às 19h
    scheduler.add_job(
        _agendar_post,
        CronTrigger(day_of_week="wed,fri", hour=19, minute=0),
        args=["Onírico", "Reflexão do dia - Onírico"],
        id="onirico_quarta_sexta",
        replace_existing=True,
    )
    # Pneuma: todo dia às 6h
    scheduler.add_job(
        _agendar_post,
        CronTrigger(day_of_week="*", hour=6, minute=0),
        args=["Pneuma", "Reflexão do dia - Pneuma"],
        id="pneuma_diario",
        replace_existing=True,
    )
    logger.info("Agendamentos configurados: Polis (ter/qui 8h), Onírico (qua/sex 19h), Pneuma (diário 6h)")

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

def init_app(app):
    """Inicializa o scheduler e registra o blueprint no app Flask."""
    app.register_blueprint(instagram_bp)
    iniciar_scheduler()