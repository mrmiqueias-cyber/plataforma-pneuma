from playwright.sync_api import sync_playwright
import time


def main():
    print("Iniciando teste de sessão do Instagram...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )

        context = browser.new_context(
            storage_state="instagram_state.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="pt-BR",
        )

        page = context.new_page()

        # Script anti-detecção para remover a flag webdriver
        page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """
        )

        print("Carregando instagram.com...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")

        print("Aguardando 5 segundos...")
        time.sleep(5)

        print("Capturando screenshot...")
        page.screenshot(path="teste_sessao.png")

        url_atual = page.url
        conteudo = page.content().lower()

        # Verifica se ainda está logado
        logado = (
            "accounts/login" not in url_atual
            and "login" not in url_atual
            and ("notificacoes" in conteudo or "notifications" in conteudo or "feed" in conteudo)
        )

        if logado:
            print("SUCESSO: A sessão salva ainda funciona! Você está logado no Instagram.")
        else:
            print("FALHA: A sessão salva não funciona mais. É necessário fazer login novamente.")

        print(f"URL atual: {url_atual}")
        print("Mantendo o navegador aberto por 20 segundos para confirmação visual...")
        time.sleep(20)

        context.close()
        browser.close()
        print("Navegador fechado. Teste finalizado.")


if __name__ == "__main__":
    main()