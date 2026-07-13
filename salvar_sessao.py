from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    navegador = p.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
    )
    contexto = navegador.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    pagina = contexto.new_page()
    
    # Remove rastros de automação
    pagina.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.chrome = { runtime: {} };
    """)
    
    pagina.goto("https://www.instagram.com/")
    
    input("👉 FAZ O LOGIN MANUALMENTE no Instagram que abriu.\nDepois que entrar, volta aqui e aperta ENTER...")
    
    contexto.storage_state(path="instagram_state.json")
    print("✅ Sessão salva em instagram_state.json")
    navegador.close()