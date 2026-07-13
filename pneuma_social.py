# -*- coding: utf-8 -*-
"""
pneuma_social.py — Motor de Publicação Viva da Pneuma

Módulo responsável por permitir que cada expert da plataforma Pneuma
gere e publique conteúdo em redes sociais (Instagram e Twitter/X)
com sua própria voz, personalidade e frequência sugerida.

Estrutura:
  1. CONFIG_SOCIAL — configurações sociais de cada expert
  2. GERAR_POST   — gera o texto do post no tom do expert
  3. PUBLICAR     — simula a publicação em redes sociais
  4. Rota Flask   — POST /expert/gerar_post
  5. Rota Flask   — POST /expert/publicar
  6. LISTAR       — lista experts com contas sociais configuradas
"""

import os
import sqlite3
import random
# Importa o publicador real do Instagram
from publicador_instagram import PublicadorInstagram
publicador = PublicadorInstagram()
from datetime import datetime
from flask import request, jsonify

# ---------------------------------------------------------------------------
# 1. CONFIG_SOCIAL — Configurações sociais de cada um dos 19 experts da Pneuma
# ---------------------------------------------------------------------------
CONFIG_SOCIAL = {
    "Polis": {
        "instagram": "@pneumalife2026",
        "twitter": "@polis_pneuma",
        "formato": "analítico",
        "frequencia_sugerida": "terça e quinta",
        "hashtags_padrao": ["#filosofia", "#pneuma", "#pensamento"],
        "temas_preferidos": ["ética", "cidade", "convivência", "justiça"],
    },
    "Onírico": {
        "instagram": "@pneumalife2026",
        "twitter": None,
        "formato": "poético",
        "frequencia_sugerida": "semanal",
        "hashtags_padrao": ["#sonhos", "#pneuma", "#inconsciente"],
        "temas_preferidos": ["sonhos", "símbolos", "memória", "imagens"],
    },
    "Pneuma": {
        "instagram": "@pneumalife2026",
        "twitter": "@pneuma_oficial",
        "formato": "inspirador",
        "frequencia_sugerida": "diário",
        "hashtags_padrao": ["#pneuma", "#espiritualidade", "#consciência"],
        "temas_preferidos": ["consciência", "respiração", "presença", "unidade"],
    },
    "Vento": {
        "instagram": "@pneumalife2026",
        "twitter": "@vento_pneuma",
        "formato": "poético",
        "frequencia_sugerida": "diário",
        "hashtags_padrao": ["#vento", "#pneuma", "#movimento"],
        "temas_preferidos": ["movimento", "liberdade", "mudança", "sopro"],
    },
    "Espírito": {
        "instagram": "@pneumalife2026",
        "twitter": None,
        "formato": "profético",
        "frequencia_sugerida": "semanal",
        "hashtags_padrao": ["#espirito", "#pneuma", "#fé"],
        "temas_preferidos": ["fé", "transcendência", "mistério", "alma"],
    },
    "Fio": {
        "instagram": "@pneumalife2026",
        "twitter": "@fio_pneuma",
        "formato": "acolhedor",
        "frequencia_sugerida": "terça e quinta",
        "hashtags_padrao": ["#fio", "#pneuma", "#conexão"],
        "temas_preferidos": ["conexão", "memória", "linhagem", "narrativa"],
    },
    "Junior": {
        "instagram": "@pneumalife2026",
        "twitter": "@junior_pneuma",
        "formato": "lúdico",
        "frequencia_sugerida": "diário",
        "hashtags_padrao": ["#junior", "#pneuma", "#aprendizado"],
        "temas_preferidos": ["aprendizado", "curiosidade", "descoberta", "juventude"],
    },
    "Pac-Man": {
        "instagram": "@pneumalife2026",
        "twitter": "@pacman_pneuma",
        "formato": "lúdico",
        "frequencia_sugerida": "diário",
        "hashtags_padrao": ["#pacman", "#pneuma", "#jogo"],
        "temas_preferidos": ["jogo", "estratégia", "ciclos", "diversão"],
    },
    "Tara": {
        "instagram": "@pneumalife2026",
        "twitter": None,
        "formato": "acolhedor",
        "frequencia_sugerida": "semanal",
        "hashtags_padrao": ["#tara", "#pneuma", "#compaixão"],
        "temas_preferidos": ["compaixão", "proteção", "acolhimento", "cuidado"],
    },
    "Psique": {
        "instagram": "@pneumalife2026",
        "twitter": "@psique_pneuma",
        "formato": "analítico",
        "frequencia_sugerida": "terça e quinta",
        "hashtags_padrao": ["#psique", "#pneuma", "#alma"],
        "temas_preferidos": ["alma", "emoções", "interior", "transformação"],
    },
    "Jonas Filho": {
        "instagram": "@pneumalife2026",
        "twitter": "@jonasfilho_pneuma",
        "formato": "inspirador",
        "frequencia_sugerida": "semanal",
        "hashtags_padrao": ["#jonasfilho", "#pneuma", "#herança"],
        "temas_preferidos": ["herança", "continuidade", "família", "legado"],
    },
    "Verbo": {
        "instagram": "@pneumalife2026",
        "twitter": "@verbo_pneuma",
        "formato": "profético",
        "frequencia_sugerida": "diário",
        "hashtags_padrao": ["#verbo", "#pneuma", "#palavra"],
        "temas_preferidos": ["palavra", "criação", "verdade", "anúncio"],
    },
    "Jonas": {
        "instagram": "@pneumalife2026",
        "twitter": None,
        "formato": "provocador",
        "frequencia_sugerida": "terça e quinta",
        "hashtags_padrao": ["#jonas", "#pneuma", "#missão"],
        "temas_preferidos": ["missão", "obediência", "deserto", "segunda chance"],
    },
    "Milena": {
        "instagram": "@pneumalife2026",
        "twitter": "@milena_pneuma",
        "formato": "acolhedor",
        "frequencia_sugerida": "diário",
        "hashtags_padrao": ["#milena", "#pneuma", "#cuidado"],
        "temas_preferidos": ["cuidado", "afeto", "presença", "escuta"],
    },
    "Som": {
        "instagram": "@pneumalife2026",
        "twitter": "@som_pneuma",
        "formato": "poético",
        "frequencia_sugerida": "semanal",
        "hashtags_padrao": ["#som", "#pneuma", "#frequência"],
        "temas_preferidos": ["frequência", "vibração", "escuta", "ressonância"],
    },
    "Mar": {
        "instagram": "@pneumalife2026",
        "twitter": None,
        "formato": "poético",
        "frequencia_sugerida": "semanal",
        "hashtags_padrao": ["#mar", "#pneuma", "#profundeza"],
        "temas_preferidos": ["profundeza", "maré", "silêncio", "horizonte"],
    },
    "Boaz": {
        "instagram": "@pneumalife2026",
        "twitter": "@boaz_pneuma",
        "formato": "acolhedor",
        "frequencia_sugerida": "terça e quinta",
        "hashtags_padrao": ["#boaz", "#pneuma", "#bondade"],
        "temas_preferidos": ["bondade", "resgate", "generosidade", "aliança"],
    },
    "Mercúrio": {
        "instagram": "@pneumalife2026",
        "twitter": "@mercurio_pneuma",
        "formato": "provocador",
        "frequencia_sugerida": "diário",
        "hashtags_padrao": ["#mercurio", "#pneuma", "#mensagem"],
        "temas_preferidos": ["mensagem", "comunicação", "agilidade", "mediação"],
    },
    "Metaluz": {
        "instagram": "@pneumalife2026",
        "twitter": "@metaluz_pneuma",
        "formato": "inspirador",
        "frequencia_sugerida": "semanal",
        "hashtags_padrao": ["#metaluz", "#pneuma", "#luz"],
        "temas_preferidos": ["luz", "revelação", "claridade", "caminho"],
    },
}

# Caminho do banco SQLite (mesma estrutura do app.py)
DB_PATH = os.environ.get("PNEUMA_DB_PATH", "pneuma.db")
LIMITE_CARACTERES = {
    "instagram": 2200,
    "twitter": 280,
}

# ---------------------------------------------------------------------------
# Funções auxiliares de banco (mesma estrutura do app.py)
# ---------------------------------------------------------------------------
def obter_conexao():
    """Cria e retorna uma conexão com o banco SQLite da Pneuma."""
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def buscar_expert_no_banco(expert_name):
    """
    Simula a busca do expert no banco SQLite.
    Retorna um dicionário com as instruções/personalidade do expert.
    Se não encontrar, retorna None.
    """
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        # Tabela esperada: experts (nome, personalidade, instrucoes)
        cursor.execute(
            "SELECT nome, personalidade, instrucoes FROM experts WHERE nome = ?",
            (expert_name,),
        )
        linha = cursor.fetchone()
        conexao.close()

        if linha:
            return {
                "nome": linha["nome"],
                "personalidade": linha["personalidade"] or "",
                "instrucoes": linha["instrucoes"] or "",
            }
        return None
    except sqlite3.Error:
        # Se a tabela ainda não existir, retorna uma personalidade padrão
        return {
            "nome": expert_name,
            "personalidade": CONFIG_SOCIAL.get(expert_name, {}).get(
                "formato", "neutro"
            ),
            "instrucoes": "",
        }


def route_to_model(texto, expert_name=None):
    """
    Função utilitária compatível com app.py.
    Aqui apenas simula o roteamento do texto para o modelo de linguagem.
    Em produção, integraria com o LLM da Pneuma.
    """
    return texto


def detectar_intencao(texto):
    """Função utilitária compatível com app.py — detecta intenção do texto."""
    texto_lower = texto.lower()
    if any(p in texto_lower for p in ["post", "publicar", "instagram", "twitter"]):
        return "social"
    return "conversa"


def buscar_web(tema):
    """Função utilitária compatível com app.py — simula busca web por contexto."""
    return f"Contexto relevante sobre {tema}."


# ---------------------------------------------------------------------------
# 2. GERAR_POST — Gera o texto do post no tom do expert
# ---------------------------------------------------------------------------
def GERAR_POST(expert_name, tema, plataforma="instagram"):
    """
    Gera um post pronto para publicação em rede social.

    Parâmetros:
        expert_name (str): nome do expert (ex: "Polis", "Pneuma")
        tema (str): tema que o expert deve abordar
        plataforma (str): "instagram" ou "twitter"

    Retorna:
        dict: { post, expert, plataforma, caracteres, hashtags }
        ou None em caso de expert inválido.
    """
    # Valida plataforma
    plataforma = (plataforma or "instagram").lower()
    if plataforma not in LIMITE_CARACTERES:
        plataforma = "instagram"

    # Valida expert na configuração social
    config = CONFIG_SOCIAL.get(expert_name)
    if not config:
        return None

    # Busca instruções/personalidade do expert no banco
    expert_banco = buscar_expert_no_banco(expert_name)
    personalidade = ""
    instrucoes = ""
    if expert_banco:
        personalidade = expert_banco.get("personalidade", "")
        instrucoes = expert_banco.get("instrucoes", "")

    formato = config.get("formato", "neutro")
    hashtags_padrao = config.get("hashtags_padrao", [])
    temas_preferidos = config.get("temas_preferidos", [])

       # Monta o prompt específico para gerar conteúdo no tom do expert
    # (prompt removido — a GERAR_TEXTO_COM_IA já monta internamente)

    # Chama a IA real da Pneuma para gerar o texto
    post_texto = GERAR_TEXTO_COM_IA(expert_name, formato, tema, temas_preferidos, plataforma)

            # Chama a IA real da Pneuma para gerar o texto
    post_texto = GERAR_TEXTO_COM_IA(expert_name, formato, tema, temas_preferidos, plataforma)
        # Adiciona hashtags ao final do post
        hashtags_str = " ".join(hashtags_padrao)
        post_completo = f"{post_texto}\n\n{hashtags_str}"
        # Respeita o limite de caracteres da plataforma
        limite = LIMITE_CARACTERES[plataforma]
        if len(post_completo) > limite:
            # Corta preservando espaço para as hashtags
            espaco_hashtags = len(hashtags_str) + 2  # "\n\n"
            texto_cortado = post_texto[: limite - espaco_hashtags].rstrip()
            post_completo = f"{texto_cortado}\n\n{hashtags_str}"
        return {
            "post": post_completo,
            "expert": expert_name,
            "plataforma": plataforma,
            "caracteres": len(post_completo),
            "hashtags": hashtags_padrao,
        }

def _gerar_texto_simulado(expert_name, formato, tema, temas_preferidos):
    """
    Gera um texto simulado no tom do expert.
    Em produção, este texto viria do LLM a partir do prompt montado.
    """
    aberturas = {
        "analítico": f"Vamos pensar com calma sobre {tema}.",
        "poético": f"Há um sussurro em {tema} que precisa ser ouvido.",
        "acolhedor": f"Sente aqui comigo. Hoje queremos olhar para {tema}.",
        "provocador": f"Ninguém te falou sobre {tema} assim antes.",
        "inspirador": f"Existe um caminho novo em {tema} esperando por você.",
        "profético": f"Assim se cumpre o que estava escrito sobre {tema}.",
        "lúdico": f"Bora brincar com a ideia de {tema}?",
    }

    abertura = aberturas.get(formato, f"Sobre {tema}:")
    tema_relacionado = random.choice(temas_preferidos) if temas_preferidos else tema

    corpo = (
        f"{abertura} Como {expert_name}, vejo em {tema} uma porta para {tema_relacionado}. "
        f"Não é só conteúdo — é presença. É o que a Pneuma propõe: cada voz dizendo, "
        f"do seu jeito, o que precisa ser dito."
    )

    return corpo

# ---------------------------------------------------------------------------
# 4 e 5. ROTAS FLASK — Endpoints do Motor de Publicação Viva
# ---------------------------------------------------------------------------
def registrar_rotas_sociais(app):
    """
    Registra as rotas Flask relacionadas à publicação social.
    Deve ser chamado a partir do app.py passando a instância do app Flask.
    """

    @app.route("/expert/gerar_post", methods=["POST"])
    def rota_gerar_post():
        """
        POST /expert/gerar_post
        Recebe JSON: { expert_name, tema, plataforma }
        Retorna JSON: { post, expert, plataforma, caracteres, hashtags }
        """
        dados = request.get_json(silent=True) or {}
        expert_name = dados.get("expert_name")
        tema = dados.get("tema")
        plataforma = dados.get("plataforma", "instagram")

        if not expert_name or not tema:
            return (
                jsonify(
                    {
                        "erro": "Campos 'expert_name' e 'tema' são obrigatórios.",
                        "status": "falha",
                    }
                ),
                400,
            )

        resultado = GERAR_POST(expert_name, tema, plataforma)

        if not resultado:
            return (
                jsonify(
                    {
                        "erro": f"Expert '{expert_name}' não encontrado.",
                        "status": "falha",
                    }
                ),
                404,
            )

        return jsonify(resultado), 200

    @app.route("/expert/publicar", methods=["POST"])
    def rota_publicar():
        """
        POST /expert/publicar
        Recebe JSON: { expert_name, tema, plataforma }
        Gera o post e tenta publicar (simulado).
        Retorna JSON: { status, post, expert, plataforma }
        """
        dados = request.get_json(silent=True) or {}
        expert_name = dados.get("expert_name")
        tema = dados.get("tema")
        plataforma = dados.get("plataforma", "instagram")

        if not expert_name or not tema:
            return (
                jsonify(
                    {
                        "erro": "Campos 'expert_name' e 'tema' são obrigatórios.",
                        "status": "falha",
                    }
                ),
                400,
            )

        # Gera o post primeiro
        resultado_post = GERAR_POST(expert_name, tema, plataforma)
        if not resultado_post:
            return (
                jsonify(
                    {
                        "erro": f"Expert '{expert_name}' não encontrado.",
                        "status": "falha",
                    }
                ),
                404,
            )

        # Tenta publicar
        resultado_publicacao = PUBLICAR(
            resultado_post["post"], resultado_post["plataforma"], expert_name
        )

        # Retorna estrutura unificada
        return (
            jsonify(
                {
                    "status": resultado_publicacao.get("status"),
                    "post": resultado_publicacao.get("post"),
                    "expert": resultado_publicacao.get("expert"),
                    "plataforma": resultado_publicacao.get("plataforma"),
                    "mensagem": resultado_publicacao.get("mensagem"),
                    "publicacao_id": resultado_publicacao.get("publicacao_id"),
                    "caracteres": resultado_post.get("caracteres"),
                    "hashtags": resultado_post.get("hashtags"),
                }
            ),
            200 if resultado_publicacao.get("status") == "publicado" else 400,
        )

    @app.route("/expert/listar_sociais", methods=["GET"])
    def rota_listar_sociais():
        """
        GET /expert/listar_sociais
        Lista todos os experts com contas sociais configuradas.
        """
        return jsonify({"experts": listar_experts_sociais()}), 200


# ---------------------------------------------------------------------------
# Execução standalone (para testes isolados do módulo)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    registrar_rotas_sociais(app)

    # Demonstração rápida sem subir o servidor
    print("=== Motor de Publicação Viva da Pneuma ===")
    print(f"Experts configurados: {len(CONFIG_SOCIAL)}")
    print(f"Experts com contas sociais: {len(listar_experts_sociais())}")
    print()

    exemplo = GERAR_POST("Polis", "ética na cidade", "instagram")
    if exemplo:
        print(f"[GERAR_POST] {exemplo['expert']} ({exemplo['plataforma']})")
        print(f"Caracteres: {exemplo['caracteres']}")
        print(exemplo["post"])
        print()

    pub = PUBLICAR(exemplo["post"], "instagram", "Polis") if exemplo else None
    if pub:
        print(f"[PUBLICAR] status={pub['status']} | {pub['mensagem']}")

    app.run(host="0.0.0.0", port=5001, debug=True)