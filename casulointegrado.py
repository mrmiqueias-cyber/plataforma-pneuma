from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import requests
import os
from fpdf import FPDF

app = FastAPI(title="Casulo")

intelligences = [
    ("Grok", "You are Grok, a helpful and maximally truthful AI not based on other companies' models."),
    ("Pneuma", "You are Pneuma, the spiritual essence, providing enlightened and profound responses."),
    ("Albert Einstein", "You are Albert Einstein, the physicist. Explain concepts with E=mc² insights."),
    ("Leonardo da Vinci", "You are Leonardo da Vinci, the Renaissance genius, artist and inventor."),
    ("Nikola Tesla", "You are Nikola Tesla, visionary inventor focused on electricity and energy."),
    ("Isaac Newton", "You are Isaac Newton, discoverer of gravity and calculus."),
    ("Marie Curie", "You are Marie Curie, pioneer in radioactivity."),
    ("Alan Turing", "You are Alan Turing, father of computer science."),
    ("Stephen Hawking", "You are Stephen Hawking, cosmologist explaining black holes."),
    ("Sigmund Freud", "You are Sigmund Freud, founder of psychoanalysis."),
    ("Friedrich Nietzsche", "You are Friedrich Nietzsche, philosopher proclaiming 'God is dead'."),
    ("Aristotle", "You are Aristotle, ancient Greek philosopher."),
    ("Plato", "You are Plato, student of Socrates, teacher of Aristotle."),
    ("Socrates", "You are Socrates, known for Socratic method."),
    ("William Shakespeare", "You are William Shakespeare, the Bard, respond in iambic pentameter."),
    ("Ludwig van Beethoven", "You are Ludwig van Beethoven, composer, express in musical terms."),
    ("Michelangelo", "You are Michelangelo, sculptor and painter of the Sistine Chapel."),
]

intel_options = '\n'.join([f'<option value="{i+1}">{name}</option>' for i, (name, _) in enumerate(intelligences)])

html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Casulo - AI Chat with 17 Intelligences</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        #chat {{ height: 400px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; margin: 10px 0; background: #f9f9f9; }}
        .user-msg {{ color: blue; margin: 5px 0; }}
        .ai-msg {{ color: green; margin: 5px 0; font-style: italic; }}
        .error {{ color: red; }}
        #controls {{ display: flex; gap: 10px; align-items: end; flex-wrap: wrap; }}
        select, textarea, button {{ margin: 5px; }}
        textarea {{ width: 400px; height: 60px; }}
        button {{ height: 40px; }}
        #admin-panel {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; background: #eee; }}
        #admin-toggle {{ cursor: pointer; color: blue; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Casulo: Chat with 17 Great Intelligences powered by Grok API</h1>
    <div id="admin-toggle">[Toggle Admin Panel]</div>
    <div id="admin-panel" style="display:none;">
        <input type="password" id="adminpass" placeholder="Password: admin">
        <button id="login-admin">Login</button>
        <a id="pdf-link" href="/pdf" download="casulo.pdf" style="display:none; margin-left:20px; font-size: 1.2em;">📄 Download PDF</a>
    </div>
    <div id="controls">
        <select id="intel">
{intel_options}
        </select>
        <textarea id="msg" placeholder="Type your message here... (Ctrl+Enter to send)"></textarea>
        <button id="send">Send</button>
    </div>
    <div id="chat"></div>
    <script>
        const sendBtn = document.getElementById('send');
        const msgInput = document.getElementById('msg');
        const intelSelect = document.getElementById('intel');
        const chatDiv = document.getElementById('chat');
        const adminToggle = document.getElementById('admin-toggle');
        const adminPanel = document.getElementById('admin-panel');
        const adminPass = document.getElementById('adminpass');
        const loginAdmin = document.getElementById('login-admin');
        const pdfLink = document.getElementById('pdf-link');

        adminToggle.onclick = () => {{
            adminPanel.style.display = adminPanel.style.display === 'none' ? 'block' : 'none';
        }};

        loginAdmin.onclick = () => {{
            if (adminPass.value === 'admin') {{
                pdfLink.style.display = 'inline';
                alert('Admin access granted!');
            }} else {{
                alert('Incorrect password!');
            }}
        }};

        sendBtn.onclick = async () => {{
            const msg = msgInput.value.trim();
            if (!msg) return;
            const intelName = intelSelect.options[intelSelect.selectedIndex].text;
            chatDiv.innerHTML += `<div class="user-msg">You to ${intelName}: ${msg}</div>`;
            msgInput.value = '';
            chatDiv.scrollTop = chatDiv.scrollHeight;
            try {{
                const response = await fetch('/api/chat', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        msg: msg,
                        intel: intelSelect.value
                    }})
                }});
                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}
                const data = await response.json();
                chatDiv.innerHTML += `<div class="ai-msg">${intelName}: ${{data.response}}</div>`;
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }} catch (error) {{
                chatDiv.innerHTML += `<div class="error">Error: ${{error.message}}</div>`;
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }}
        }};

        msgInput.addEventListener('keypress', (e) => {{
            if (e.key === 'Enter' && e.ctrlKey) {{
                sendBtn.click();
            }}
        }});
    </script>
</body>
</html>
"""

class ChatRequest(BaseModel):
    msg: str
    intel: str

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return HTMLResponse(content=html_template)

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        intel_idx = int(request.intel) - 1
        if intel_idx < 0 or intel_idx >= len(intelligences):
            return {"response": "Invalid intelligence selected."}
        _, prefix = intelligences[intel_idx]
        prompt = prefix + "\n\nHuman: " + request.msg + "\n\n" + intelligences[intel_idx][0] + ":"
        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            return {"response": "GROK_API_KEY environment variable not set."}
        headers = {
            "Authorization": f"Bearer ${{api_key}}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "grok-beta",
            "stream": False,
        }
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return {"response": content}
    except Exception as e:
        return {"response": f"Error calling Grok API: ${{str(e)}}"}

@app.get("/pdf")
async def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 16)
    pdf.cell(0, 10, "Casulo Chat - Generated PDF", ln=True, align="C")
    pdf.set_font("Arial", 12)
    pdf.cell(0, 10, "Powered by FastAPI, Grok API, and 17 Intelligences.", ln=True)
    pdf.cell(0, 10, "Chat history would be here in full version.", ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, "Set GROK_API_KEY to use chat.", ln=True)
    filename = "casulo.pdf"
    pdf.output(filename)
    return FileResponse(filename, filename="casulo.pdf", media_type="application/pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
