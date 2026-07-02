# expertchat.py
import sqlite3
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import time
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    expert_id: str
    message: str
    stream: bool = False

def get_expert_response(expert_id: str, message: str) -> str:
    experts = {
        "grok": "Grok responde: " + message,
        "llama": "Llama responde: " + message,
        "claude": "Claude responde: " + message,
        "gpt4": "GPT-4 responde: " + message,
    }
    resp = experts.get(expert_id.lower())
    if not resp:
        raise HTTPException(status_code=400, detail="Expert não encontrado")
    return resp

def generate_stream(expert_id: str, message: str):
    full_resp = get_expert_response(expert_id, message)
    for i in range(0, len(full_resp), 5):
        chunk = full_resp[i:i+5]
        yield f"data: {json.dumps({'chunk': chunk})}\\n\\n"
        time.sleep(0.05)

@router.post("/expertchat")
async def expertchat(request: ChatRequest):
    expert_id = request.expert_id
    message = request.message
    if request.stream:
        return StreamingResponse(generate_stream(expert_id, message), media_type="text/event-stream")
    response = get_expert_response(expert_id, message)
    conn = sqlite3.connect("chaos.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expert_id TEXT,
            message TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("INSERT INTO chats (expert_id, message, response) VALUES (?, ?, ?)", (expert_id, message, response))
    conn.commit()
    conn.close()
    return {"response": response}

# expertvalidacao.py
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ValidationRequest(BaseModel):
    expert_id: str

def get_expert_response(expert_id: str, message: str) -> str:
    experts = {
        "grok": "Grok responde: " + message,
        "llama": "Llama responde: " + message,
        "claude": "Claude responde: " + message,
        "gpt4": "GPT-4 responde: " + message,
    }
    resp = experts.get(expert_id.lower())
    if not resp:
        raise HTTPException(status_code=400, detail="Expert não encontrado")
    return resp

@router.post("/expertvalidacao")
async def expertvalidacao(request: ValidationRequest):
    expert_id = request.expert_id
    test_message = "Teste de reconhecimento de simbologia e DNA."
    response = get_expert_response(expert_id, test_message)
    simbologia_ok = "simbologia" in response.lower()
    dna_ok = "dna" in response.lower()
    status = "ok" if simbologia_ok and dna_ok else "erro"
    details = {
        "simbologia": simbologia_ok,
        "dna": dna_ok,
        "response": response
    }
    conn = sqlite3.connect("chaos.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS validacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expert_id TEXT,
            status TEXT,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    import json
    c.execute("INSERT INTO validacoes (expert_id, status, details) VALUES (?, ?, ?)",
              (expert_id, status, json.dumps(details)))
    conn.commit()
    conn.close()
    return {"status": status, "details": details}
