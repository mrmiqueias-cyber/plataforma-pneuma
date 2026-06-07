# PATCH: Adiciona salvamento no casulo_chats

# No endpoint /expert/chat, DEPOIS de receber a resposta:
# Adicionar este código:

def save_casulo_chat(expert_id, role, content):
    """Salva mensagem no casulo_chats"""
    try:
        conn = sqlite3.connect('casulo.db', timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        c = conn.cursor()
        c.execute(
            "INSERT INTO casulo_chats (expert_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (expert_id, role, content, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar no casulo_chats: {str(e)}")
        return False

# Depois de receber a resposta do Expert:
# save_casulo_chat(expert_id, 'user', user_message)
# save_casulo_chat(expert_id, 'expert', response)

