"""
pneuma_ferramentas.py — Módulo de ferramentas externas para os Experts da Pneuma.
"""

import io
import re
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

try:
    from duckduckgo_search import DDGS
except Exception:  # pragma: no cover
    DDGS = None

logger = logging.getLogger(__name__)


def detectar_intencao(mensagem: str) -> str:
    """Detecta a intenção do usuário a partir do texto da mensagem.

    Retorna uma string categorizando a intenção:
    - 'codigo' quando parece haver código a executar
    - 'busca' quando parece haver pedido de busca na web
    - 'conversa' caso contrário
    """
    if not isinstance(mensagem, str) or not mensagem.strip():
        return "conversa"

    texto = mensagem.lower()

    marcadores_codigo = [
        "executar codigo",
        "executa codigo",
        "rode esse codigo",
        "rodar codigo",
        "python",
        "print(",
        "def ",
        "```python",
        "```py",
        "import ",
        "html",
        "<!doctype html",
        "<html",
    ]

    marcadores_busca = [
        "buscar",
        "busca",
        "pesquisar",
        "pesquisa",
        "procurar",
        "google",
        "duckduckgo",
        "o que é",
        "o que e",
        "quem é",
        "quem e",
        "noticias",
        "notícia",
    ]

    for marcador in marcadores_codigo:
        if marcador in texto:
            return "codigo"

    for marcador in marcadores_busca:
        if marcador in texto:
            return "busca"

    return "conversa"


def buscar_web(query: str, max_resultados: int = 5) -> list:
    """Busca na web usando DuckDuckGo. Tenta DDGS primeiro, fallback requests+BeautifulSoup."""
    if not isinstance(query, str) or not query.strip():
        return []

    # Tenta com DDGS (duckduckgo_search) — mais confiável
    if DDGS is not None:
        try:
            resultados = []
            with DDGS() as ddgs:
                for i, r in enumerate(ddgs.text(query, max_results=max_resultados)):
                    if i >= max_resultados:
                        break
                    resultados.append({
                        'titulo': r.get('title', ''),
                        'url': r.get('href', ''),
                        'resumo': r.get('body', ''),
                    })
            if resultados:
                return resultados
        except Exception as e:
            print(f"[buscar_web] DDGS falhou: {e}")

    # Fallback: requests + BeautifulSoup
    import requests
    from bs4 import BeautifulSoup
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            headers=headers,
            data={"q": query},
            timeout=15
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        resultados = []
        for result in soup.select('.result')[:max_resultados]:
            titulo_el = result.select_one('.result__title a')
            snippet_el = result.select_one('.result__snippet')
            if titulo_el:
                resultados.append({
                    'titulo': titulo_el.get_text(strip=True),
                    'url': titulo_el.get('href', ''),
                    'resumo': snippet_el.get_text(strip=True) if snippet_el else ''
                })
        return resultados
    except Exception as e:
        print(f"[buscar_web] ERRO no fallback: {e}")
        return []

def _limpar_code_fence(texto: str) -> str:
    """Remove cercas de bloco de código (```...```) do texto informado."""
    if not isinstance(texto, str):
        return ""

    texto = texto.strip()

    padrao = re.compile(r"^```[a-zA-Z0-9_+-]*\n(.*?)```$", re.DOTALL)
    correspondencia = padrao.match(texto)
    if correspondencia:
        return correspondencia.group(1).strip()

    if texto.startswith("```") and texto.endswith("```"):
        interno = texto[3:-3].strip()
        if interno.startswith("python"):
            interno = interno[len("python"):].strip()
        elif interno.startswith("py"):
            interno = interno[len("py"):].strip()
        elif interno.startswith("html"):
            interno = interno[len("html"):].strip()
        return interno

    return texto


def _executar_python(codigo: str) -> str:
    """Executa código Python em um namespace restrito e captura a saída padrão.

    Usa io.StringIO para redirecionar stdout. Retorna a saída como string.
    """
    if not isinstance(codigo, str) or not codigo.strip():
        return ""

    codigo_limpo = _limpar_code_fence(codigo)
    buffer = io.StringIO()
    namespace: Dict[str, Any] = {"__name__": "__main__", "__builtins__": __builtins__}

    try:
        compiled = compile(codigo_limpo, "<pneuma_exec>", "exec")
    except SyntaxError as exc:
        return f"Erro de sintaxe: {exc}"

    try:
        import contextlib
        with contextlib.redirect_stdout(buffer):
            exec(compiled, namespace)
    except Exception as exc:
        saida = buffer.getvalue()
        return f"{saida}\nErro durante execução: {exc}".strip()

    return buffer.getvalue()


def _parece_html(texto: str) -> bool:
    """Verifica heuristicamente se o texto parece ser HTML."""
    if not isinstance(texto, str) or not texto.strip():
        return False

    texto_lower = texto.strip().lower()

    if texto_lower.startswith("<!doctype html"):
        return True
    if texto_lower.startswith("<html"):
        return True

    tags_comuns = ["<div", "<span", "<p>", "<p ", "<h1", "<h2", "<ul", "<ol", "<table"]
    contador = sum(1 for tag in tags_comuns if tag in texto_lower)
    return contador >= 2


def _executar_html(codigo: str) -> str:
    """Processa código HTML e retorna uma representação simples para inspeção.

    Não renderiza o HTML; apenas valida e retorna o conteúdo limpo.
    """
    if not isinstance(codigo, str) or not codigo.strip():
        return ""

    codigo_limpo = _limpar_code_fence(codigo)
    if not _parece_html(codigo_limpo):
        return "O código fornecido não parece ser HTML válido."

    return codigo_limpo.strip()


def executar_codigo(codigo: str, linguagem: str = "python") -> str:
    """Executa código de acordo com a linguagem informada.

    Suporta 'python' e 'html'. Retorna a saída/resultado como string.
    """
    if not isinstance(codigo, str) or not codigo.strip():
        return "Código vazio."

    linguagem = (linguagem or "python").strip().lower()

    if linguagem in ("python", "py", "python3"):
        return _executar_python(codigo)
    if linguagem in ("html", "htm"):
        return _executar_html(codigo)

    return f"Linguagem '{linguagem}' não suportada pela ferramenta executar_codigo."


def extrair_codigo_da_mensagem(mensagem: str) -> Tuple[Optional[str], Optional[str]]:
    """Extrai bloco de código e linguagem de uma mensagem.

    Retorna uma tupla (linguagem, codigo). Se não houver bloco, retorna (None, None).
    """
    if not isinstance(mensagem, str) or not mensagem.strip():
        return None, None

    padrao = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", re.DOTALL)
    correspondencia = padrao.search(mensagem)
    if correspondencia:
        linguagem = correspondencia.group(1).strip().lower() or None
        codigo = correspondencia.group(2).strip()
        return linguagem, codigo

    if _parece_html(mensagem.strip()):
        return "html", mensagem.strip()

    linhas = mensagem.strip().splitlines()
    if any(linha.strip().startswith(("def ", "import ", "print(", "from ")) for linha in linhas):
        return "python", mensagem.strip()

    return None, None


def wrapper_com_ferramentas(mensagem: str, contexto: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Wrapper que decide qual ferramenta usar com base na mensagem.

    Retorna um dicionário com 'intencao', 'resultado' e 'ferramenta'.
    """
    contexto = contexto or {}
    intencao = detectar_intencao(mensagem)

    if intencao == "busca":
        resultados = buscar_web(mensagem)
        return {
            "intencao": intencao,
            "ferramenta": "buscar_web",
            "resultado": resultados,
        }

    if intencao == "codigo":
        linguagem, codigo = extrair_codigo_da_mensagem(mensagem)
        if codigo:
            saida = executar_codigo(codigo, linguagem or "python")
            return {
                "intencao": intencao,
                "ferramenta": "executar_codigo",
                "resultado": saida,
                "linguagem": linguagem,
            }
        return {
            "intencao": intencao,
            "ferramenta": None,
            "resultado": "Código não encontrado na mensagem.",
        }

    return {
        "intencao": intencao,
        "ferramenta": None,
        "resultado": None,
    }


class GerenciadorFerramentas:
    """Gerencia o registro e a execução das ferramentas externas da Pneuma."""

    def __init__(self) -> None:
        self.ferramentas: Dict[str, Any] = {}
        self.registrar_padroes()

    def registrar_padroes(self) -> None:
        """Registra as ferramentas padrão disponíveis."""
        self.ferramentas = {
            "detectar_intencao": detectar_intencao,
            "buscar_web": buscar_web,
            "executar_codigo": executar_codigo,
            "extrair_codigo_da_mensagem": extrair_codigo_da_mensagem,
            "wrapper_com_ferramentas": wrapper_com_ferramentas,
        }

    def registrar(self, nome: str, funcao: Any) -> None:
        """Registra uma nova ferramenta pelo nome."""
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Nome da ferramenta inválido.")
        if not callable(funcao):
            raise ValueError("Função registrada deve ser chamável.")
        self.ferramentas[nome] = funcao

    def obter(self, nome: str) -> Optional[Any]:
        """Retorna a ferramenta registrada pelo nome, ou None."""
        return self.ferramentas.get(nome)

    def listar(self) -> List[str]:
        """Lista os nomes das ferramentas registradas."""
        return list(self.ferramentas.keys())

    def executar(self, nome: str, *args: Any, **kwargs: Any) -> Any:
        """Executa uma ferramenta registrada pelo nome."""
        funcao = self.obter(nome)
        if funcao is None:
            raise KeyError(f"Ferramenta '{nome}' não registrada.")
        try:
            return funcao(*args, **kwargs)
        except Exception as exc:
            logger.error("Erro ao executar ferramenta '%s': %s", nome, exc)
            raise

    def processar_mensagem(self, mensagem: str, contexto: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Processa uma mensagem usando o wrapper de ferramentas."""
        return wrapper_com_ferramentas(mensagem, contexto)

    def to_json(self) -> str:
        """Retorna a lista de ferramentas em formato JSON."""
        return json.dumps({"ferramentas": self.listar()}, ensure_ascii=False)