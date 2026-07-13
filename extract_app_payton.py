import os
import re
from docx import Document

DOCX_FILE = "App.payton.docx"

KEYWORDS = [
    "instagram", "insta", "login", "senha", "password",
    "playwright", "browser", "page.goto", "page.fill", "page.click",
    "screenshot", "post", "publicar", "disparador", "headless",
    "chromium", "storage_state", "context", "session", "cookie",
]

SCHEDULE_KEYWORDS = ["onírico", "polis", "schedule", "agendado"]


def load_lines(path):
    """Read the .docx file and return a list of lines (paragraphs)."""
    doc = Document(path)
    lines = []
    for paragraph in doc.paragraphs:
        lines.append(paragraph.text)
    return lines


def matches_any(text, keywords):
    lowered = text.lower()
    return any(kw.lower() in lowered for kw in keywords)


def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def extract_function_blocks(lines):
    """Return list of (start_index, function_name, block_lines) for def blocks."""
    blocks = []
    current_start = None
    current_name = None
    current_block = []

    def flush():
        if current_start is not None:
            blocks.append((current_start, current_name, current_block[:80]))

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r"^def\s+", stripped):
            flush()
            current_start = idx
            match = re.match(r"^def\s+([A-Za-z0-9_]+)", stripped)
            current_name = match.group(1) if match else "<unknown>"
            current_block = [line]
        elif current_start is not None:
            current_block.append(line)
    flush()
    return blocks


def main():
    if not os.path.exists(DOCX_FILE):
        print(f"ERRO: Arquivo '{DOCX_FILE}' não encontrado no diretório atual.")
        return

    lines = load_lines(DOCX_FILE)

    # 1) Linhas que contêm as palavras-chave
    print_section("1) LINHAS QUE CONTÊM AS PALAVRAS-CHAVE")
    found_any = False
    for idx, line in enumerate(lines, start=1):
        if matches_any(line, KEYWORDS):
            found_any = True
            print(f"Linha {idx}: {line}")
    if not found_any:
        print("Nenhuma linha encontrada com as palavras-chave.")

    # 2) Blocos de função que contêm as palavras-chave
    print_section("2) BLOCOS DE FUNÇÃO (def ...) QUE CONTÊM AS PALAVRAS-CHAVE")
    blocks = extract_function_blocks(lines)
    relevant_blocks = []
    for start, name, block in blocks:
        block_text = "\n".join(block)
        if matches_any(block_text, KEYWORDS):
            relevant_blocks.append((start, name, block))

    if not relevant_blocks:
        print("Nenhum bloco de função relevante encontrado.")
    else:
        for start, name, block in relevant_blocks:
            print(f"\n--- Função '{name}' (início na linha {start + 1}) ---")
            for offset, code_line in enumerate(block[:80], start=start + 1):
                print(f"{offset:4d}: {code_line}")

    # 3a) Nomes de arquivos mencionados
    print_section("3a) ARQUIVOS MENCIONADOS NO .DOCX")
    file_pattern = re.compile(r"\b[A-Za-z0-9_]+\.(py|json|txt|env|js|ts|docx|md|yml|yaml|cfg|ini)\b")
    mentioned_files = set()
    for line in lines:
        for match in file_pattern.findall(line):
            pass
        for match in file_pattern.finditer(line):
            mentioned_files.add(match.group(0))
    if mentioned_files:
        for f in sorted(mentioned_files):
            print(f"- {f}")
    else:
        print("Nenhum nome de arquivo encontrado.")

    # 3b) Funções que fazem login no Instagram
    print_section("3b) FUNÇÕES DE LOGIN / POSTAGEM NO INSTAGRAM")
    login_keywords = ["login", "postar", "instagram", "insta"]
    login_blocks = []
    for start, name, block in blocks:
        block_text = "\n".join(block)
        if matches_any(name, login_keywords) or matches_any(block_text, login_keywords):
            login_blocks.append((start, name, block))

    if not login_blocks:
        print("Nenhuma função de login/postagem encontrada.")
    else:
        for start, name, block in login_blocks:
            print(f"\n>>> Função '{name}' (início na linha {start + 1}) <<<")
            for offset, code_line in enumerate(block[:80], start=start + 1):
                print(f"{offset:4d}: {code_line}")

    # 3c) Como INSTAGRAM_PASS e INSTAGRAM_USER são lidos
    print_section("3c) LEITURA DE INSTAGRAM_PASS / INSTAGRAM_USER")
    env_patterns = [
        re.compile(r"os\.getenv\s*\(\s*['\"]INSTAGRAM_(?:PASS|USER)['\"]\s*\)"),
        re.compile(r"os\.environ\s*\[?\s*['\"]INSTAGRAM_(?:PASS|USER)['\"]\s*\]?"),
        re.compile(r"dotenv|load_dotenv"),
        re.compile(r"INSTAGRAM_(?:PASS|USER)"),
    ]
    env_found = False
    for idx, line in enumerate(lines, start=1):
        for pattern in env_patterns:
            if pattern.search(line):
                env_found = True
                print(f"Linha {idx}: {line}")
                break
    if not env_found:
        print("Nenhuma referência a INSTAGRAM_PASS / INSTAGRAM_USER encontrada.")

    # 3d) Onde aparece "Falha no login"
    print_section("3d) OCORRÊNCIAS DE 'FALHA NO LOGIN' (com contexto de 10 linhas)")
    falha_found = False
    for idx, line in enumerate(lines):
        if "falha no login" in line.lower():
            falha_found = True
            start_ctx = max(0, idx - 5)
            end_ctx = min(len(lines), idx + 6)
            print(f"\n>>> Ocorrência na linha {idx + 1} <<<")
            for offset in range(start_ctx, end_ctx):
                marker = " >>> " if offset == idx else "     "
                print(f"{offset + 1:4d}:{marker}{lines[offset]}")
    if not falha_found:
        print("Nenhuma ocorrência de 'Falha no login' encontrada.")

    # 3e) Referências a scheduling/agendamento
    print_section("3e) REFERÊNCIAS A AGENDAMENTO / SCHEDULING")
    sched_found = False
    for idx, line in enumerate(lines, start=1):
        if matches_any(line, SCHEDULE_KEYWORDS):
            sched_found = True
            print(f"Linha {idx}: {line}")
    if not sched_found:
        print("Nenhuma referência a agendamento encontrada.")

    # 3f) Código que tira screenshot ou faz upload de imagem
    print_section("3f) CÓDIGO DE SCREENSHOT / UPLOAD DE IMAGEM")
    screenshot_keywords = ["screenshot", "upload", "set_input_files", "imagem", "foto", "image"]
    shot_found = False
    for idx, line in enumerate(lines, start=1):
        if matches_any(line, screenshot_keywords):
            shot_found = True
            print(f"Linha {idx}: {line}")
    if not shot_found:
        print("Nenhuma referência a screenshot / upload de imagem encontrada.")

    # 3g) storage_state, instagram_state.json, sessão, cookie
    print_section("3g) STORAGE_STATE / INSTAGRAM_STATE.JSON / SESSÃO / COOKIE")
    state_keywords = ["storage_state", "instagram_state.json", "sessão", "sessao", "cookie"]
    state_found = False
    for idx, line in enumerate(lines, start=1):
        if matches_any(line, state_keywords):
            state_found = True
            print(f"Linha {idx}: {line}")
    if not state_found:
        print("Nenhuma referência a storage_state / sessão / cookie encontrada.")

    print("\n" + "=" * 80)
    print("FIM DA EXTRAÇÃO")
    print("=" * 80)


if __name__ == "__main__":
    main()