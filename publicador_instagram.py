# -*- coding: utf-8 -*-
"""
publicador_instagram.py — Postagem real no Instagram via instagrapi + Pillow
"""
import os
import io
import logging
from PIL import Image, ImageDraw
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

logger = logging.getLogger(__name__)

# Cores de fundo para cada expert
CORES_EXPERT = {
    "Polis": (44, 62, 80), "Onirico": (142, 68, 173),
    "Pneuma": (39, 174, 96), "Vento": (52, 152, 219),
    "Espirito": (241, 196, 15), "Fio": (230, 126, 34),
    "Junior": (46, 204, 113), "Pac-Man": (231, 76, 60),
    "Tara": (155, 89, 182), "Psique": (52, 73, 94),
    "Jonas Filho": (26, 188, 156), "Verbo": (243, 156, 18),
    "Jonas": (100, 30, 60), "Milena": (231, 76, 60),
    "Som": (41, 128, 185), "Mar": (22, 160, 133),
    "Boaz": (133, 193, 233), "Mercurio": (241, 196, 15),
    "Metaluz": (189, 195, 199), "default": (44, 62, 80),
}

class PublicadorInstagram:
    """Gerencia login e postagem no Instagram via instagrapi."""

    def __init__(self):
        self.cl = Client()
        self.logado = False
        self.username = os.getenv("INSTAGRAM_USER", "life.pneuma")
        self.password = os.getenv("INSTAGRAM_PASS", "")

    def login(self):
        if self.logado:
            return True
        try:
            if os.path.exists("instagram_session.json"):
                self.cl.load_settings("instagram_session.json")
                self.cl.login(self.username, self.password)
                logger.info("Login via sessao salva: %s", self.username)
            else:
                self.cl.login(self.username, self.password)
                self.cl.dump_settings("instagram_session.json")
                logger.info("Login direto: %s", self.username)
            self.logado = True
            return True
        except LoginRequired:
            logger.warning("Sessao expirada. Refazendo login...")
            try:
                self.cl = Client()
                self.cl.login(self.username, self.password)
                self.cl.dump_settings("instagram_session.json")
                self.logado = True
                return True
            except Exception as e:
                logger.error("Falha no login apos expiracao: %s", e)
                return False
        except Exception as e:
            logger.error("Erro ao logar no Instagram: %s", e)
            return False

    def gerar_imagem_post(self, texto, expert_name="Pneuma"):
        """Gera imagem PNG com o texto do post (1080x1080)."""
        largura, altura = 1080, 1080
        cor_fundo = CORES_EXPERT.get(expert_name, CORES_EXPERT["default"])

        img = Image.new("RGB", (largura, altura), cor_fundo)
        draw = ImageDraw.Draw(img)
        fonte = ImageDraw.ImageFont.load_default()

        # Nome do expert no topo
        draw.text((largura/2, 100), f"✦ {expert_name} ✦",
                  fill=(255, 255, 255), font=fonte, anchor="mt")
        draw.line([(largura/2 - 80, 140), (largura/2 + 80, 140)],
                  fill=(255, 255, 255), width=2)

        # Quebra o texto em linhas
        linhas, linha_atual = [], ""
        for palavra in texto.split():
            teste = linha_atual + " " + palavra if linha_atual else palavra
            if len(teste) * 11 < (largura - 160):
                linha_atual = teste
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)

        # Desenha o texto
        y = 220
        for linha in linhas:
            draw.text((largura/2, y), linha, fill=(255, 255, 255),
                      font=fonte, anchor="mt")
            y += 45
            if y > altura - 120:
                break

        # Rodape
        draw.text((largura/2, altura - 70), "🌬️ Plataforma Pneuma",
                  fill=(200, 200, 200), font=fonte, anchor="mt")

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return img_bytes

    def postar(self, texto, expert_name="Pneuma"):
        """Publica texto + imagem no Instagram. Retorna dict com resultado."""
        if not self.login():
            return {"status": "erro", "mensagem": "Falha no login do Instagram"}

        try:
            img_bytes = self.gerar_imagem_post(texto, expert_name)
            resultado = self.cl.photo_upload(
                img_bytes, texto,
                extra_data={
                    "custom_accessibility_caption":
                    f"Post gerado pela Plataforma Pneuma — Expert: {expert_name}"
                }
            )
            return {
                "status": "publicado",
                "post": texto,
                "expert": expert_name,
                "plataforma": "instagram",
                "publicacao_id": str(resultado.id),
                "mensagem": "Post publicado com sucesso no Instagram!"
            }
        except Exception as e:
            logger.error("Erro ao publicar: %s", e)
            return {
                "status": "erro", "post": texto,
                "expert": expert_name, "plataforma": "instagram",
                "mensagem": f"Erro ao publicar: {str(e)}"
            }