# grok_wrapper.py

import os
import logging
import json
from typing import AsyncGenerator, List, Dict, Any
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def processar_camadas_sala(mensagem: str, historico: List[Dict[str, str]]) -> str:
    """
    Placeholder para processamento pelas 5 camadas da Sala dos Caos:
    1. Validação, 2. Contexto Pneuma, 3. 18 Inteligências, 4. Caos, 5. Integração.
    """
    logger.info("Processando mensagem pelas 5 camadas da Sala dos Caos...")
    # Aqui você integraria as lógicas reais das camadas
    # Exemplo simplificado:
    processed = f"[Camada 1-5 processadas] {mensagem}"
    return processed


async def chamar_grok(mensagem: str, historico: List[Dict[str, str]], contexto_sala: Dict[str, Any] = None, grok_api_key: str = None) -> AsyncGenerator[str, None]:
    """
    Wrapper para chamar a API Grok com streaming, integrando Sala dos Caos e Pneuma.
    Recebe mensagem e histórico, retorna tokens via AsyncGenerator.
    """
    try:
        # Integração com Pneuma e Sala dos Caos
        if contexto_sala:
            pneuma_prompt = contexto_sala.get('pneuma', 'Você é Grok integrado à Plataforma do Caos. Pneuma é o coração das 18 inteligências.')
            historico = [{'role': 'system', 'content': pneuma_prompt}] + historico
        
        # Processa pelas 5 camadas
        processed_mensagem = processar_camadas_sala(mensagem, historico)
        messages = historico + [{'role': 'user', 'content': processed_mensagem}]
        
        api_key = grok_api_key or os.getenv('GROK_API_KEY')
        if not api_key:
            error_msg = 'GROK_API_KEY não configurada no ambiente.'
            logger.error(error_msg)
            yield error_msg
            return
        
        client = AsyncOpenAI(api_key=api_key, base_url='https://api.x.ai/v1')
        
        stream = await client.chat.completions.create(
            model='grok-beta',
            messages=messages,
            stream=True,
            temperature=0.7
        )
        
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                logger.debug(f'Stream token: {delta}')
                yield delta
                
    except Exception as e:
        error_msg = f'Erro ao chamar Grok: {str(e)}'
        logger.error(error_msg)
        yield error_msg