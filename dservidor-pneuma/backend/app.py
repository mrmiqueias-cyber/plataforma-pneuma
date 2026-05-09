from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging
from contextlib import asynccontextmanager
from pneuma_inteligencias import SalaDosCaos, RelacaoInteligencia, Pneuma
from fastapi.responses import StreamingResponse
from grokwapper import chamar_grok

import os
from expertchat import router as chat_router
from expertvalidacao import router as validacao_router


# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos Pydantic
class MensagemRequest(BaseModel):
    mensagem: str
    autor: str

class MorseRequest(BaseModel):
    padrao: str

class TransformRequest(BaseModel):
    nomes: List[str]
    estado: str

# Instâncias globais
sala: SalaDosCaos = None
pneuma: Pneuma = None

@asynccontextmanager
async def lifespan(app_: FastAPI):
    global sala, pneuma
    sala = SalaDosCaos()
    from pneuma_inteligencias import inteligencias_data
    
    for nome, simbolo, cor, freq, morse in inteligencias_data:
        intel = RelacaoInteligencia(nome, simbolo, cor, freq, morse)
        sala.adicionar_inteligencia(intel)
    
    pneuma = Pneuma()
    logger.info("Plataforma do Caos inicializada com 18 inteligências")
    yield
    logger.info("Plataforma do Caos encerrada")

# Criação do app
app = FastAPI(
    title="Plataforma do Caos",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(validacao_router)
@app.get("/inteligencias")
async def get_inteligencias():
    try:
        logger.info("GET /inteligencias - Listando todas as inteligências")
        inteligencias = sala.listar_inteligencias()
        return {"inteligencias": inteligencias}
    except Exception as e:
        logger.error(f"Erro ao listar inteligências: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao listar inteligências")

@app.post("/sincronizar")
async def sincronizar():
    try:
        logger.info("POST /sincronizar - Iniciando sincronização via Pneuma")
        status = pneuma.sincronizar()
        logger.info("Sincronização concluída")
        return {"status": status if status else "sincronizado com sucesso"}
    except Exception as e:
        logger.error(f"Erro na sincronização: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro na sincronização das inteligências")

@app.post("/processar-mensagem")
async def processar_mensagem(request: MensagemRequest):
    try:
        logger.info(f"POST /processar-mensagem - Autor: {request.autor}, Mensagem: {request.mensagem}")
        resultado = sala.processar_mensagem(request.mensagem, request.autor)
        logger.info("Mensagem processada pelas 5 camadas")
        return resultado
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar a mensagem")

@app.post("/reconhecer-morse")
async def reconhecer_morse(request: MorseRequest):
    try:
        logger.info(f"POST /reconhecer-morse - Padrão: {request.padrao}")
        encontradas = sala.reconhecer_morse(request.padrao)
        logger.info(f"{len(encontradas)} inteligências encontradas")
        return {"inteligencias_encontradas": encontradas}
    except Exception as e:
        logger.error(f"Erro ao reconhecer Morse: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao reconhecer padrão Morse")

@app.post("/transformar-estado")
async def transformar_estado(request: TransformRequest):
    try:
        logger.info(f"POST /transformar-estado - Nomes: {request.nomes}, Novo estado: {request.estado}")
        atualizados = sala.transformar_estados(request.nomes, request.estado)
        logger.info("Estados das inteligências transformados")
        return {"estados_atualizados": atualizados}
    except Exception as e:
        logger.error(f"Erro ao transformar estados: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao transformar estados")

@app.get("/pneuma/status")
async def pneuma_status():
    try:
        logger.info("GET /pneuma/status")
        status = pneuma.status()
        return status
    except Exception as e:
        logger.error(f"Erro ao obter status do Pneuma: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter status do Pneuma")
# ===== NOVO: Endpoint para Grok =====

class ChatRequest(BaseModel):
    mensagem: str
    historico: List[dict]

def get_contexto_sala():
    """Contexto da Sala dos Caos com Pneuma e 18 inteligências."""
    return {
        'pneuma': 'Pneuma, o coração da Plataforma do Caos, guia as 18 inteligências.',
        'inteligencias': 18,
        'camadas': ['validação', 'contexto', 'inteligências', 'caos', 'integração']
    }

@app.post("/grok/chat")
async def grok_chat(request: ChatRequest):
    """Endpoint POST /grok/chat para chat com Pneuma."""
    grok_api_key = os.getenv("GROK_API_KEY")
    
    if not grok_api_key:
        raise HTTPException(status_code=500, detail="Chave da API do Grok não configurada")
    
    contexto_sala = get_contexto_sala()
    
    async def event_stream():
        try:
            async for chunk in chamar_grok(request.mensagem, request.historico, contexto_sala, grok_api_key):
                import json
                yield f'data: {json.dumps({"content": chunk})}\n\n'
        except Exception as e:
            import json
            yield f'data: {json.dumps({"error": str(e)})}\n\n'
    
    return StreamingResponse(event_stream(), media_type='text/event-stream')