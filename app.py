from flask import Flask, request, render_template, Response, send_file
from functools import wraps
import os
import qrcode
from io import BytesIO
import requests
import json
import random
import string

app = Flask(__name__)

# PIX configuration
PIX_KEY = os.getenv('PIX_KEY', 'pneuma@example.com')
PIX_MERCHANT = os.getenv('PIX_MERCHANT', 'Plataforma Pneuma')
PIX_TXID = os.getenv('PIX_TXID', 'PN3UMA00000000000000000000000001')

CASULO_PASSWORD = os.getenv('CASULO_PASSWORD', 'pneuma123')
CASULO_USERNAME = 'pneuma'


def calculate_pix_crc(payload: str) -> str:
    crc = 0xFFFF
    for char in payload:
        crc ^= ord(char) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return f'{crc:04X}'


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != CASULO_USERNAME or auth.password != CASULO_PASSWORD:
            return Response(
                'Could not verify credentials. Username: pneuma, Password from env.',
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'}
            )
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contrato')
def contrato():
    return render_template('contrato.html')


@app.route('/contribua')
def contribua():
    return render_template('contribua.html')


@app.route('/chat')
def chat_page():
    return render_template('chat.html')


@app.route('/casulo')
@requires_auth
def casulo():
    return '<h1>Casulo Pneuma</h1><p>Conte&uacute;do protegido da Plataforma Pneuma.</p>'


@app.route('/pix/qrcode')
def pix_qrcode():
    amount_str = request.args.get('amount', '0')
    try:
        amount = float(amount_str)
    except ValueError:
        amount = 0.0

    value_field = f"54{int(amount * 100):010d}" if amount > 0 else "5400000000"

    pix_key_len = len(PIX_KEY)
    merchant_len = len(PIX_MERCHANT)
    txid_len = len(PIX_TXID)

    payload = (
        "000201"
        "010212"
        f"26{len('BR.GOV.BCB.PIX'):02}BR.GOV.BCB.PIX"
        f"01{pix_key_len:02d}{PIX_KEY}"
        "52040000"
        "5303986"
        f"{value_field}"
        "5802BR"
        f"59{merchant_len:02d}{PIX_MERCHANT}"
        f"62{4 + txid_len:02d}05{txid_len:02d}{PIX_TXID}"
    )

    crc = calculate_pix_crc(payload)
    payload += crc

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


@app.route('/grok/chat', methods=['POST'])
def grok_chat():
    api_key = os.getenv('XAI_API_KEY')
    if not api_key:
        return Response("data: Error: XAI_API_KEY not set\n\n", mimetype='text/event-stream')

    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://api.x.ai/v1", api_key=api_key)
        data = request.get_json()
        messages = data.get('messages', [])

        def generate():
            stream = client.chat.completions.create(
                model="grok-beta",
                messages=messages,
                stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield f"data: {delta}\n\n"
            yield "data: [DONE]\n\n"

        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        return Response(f"data: Error: {str(e)}\n\n", mimetype='text/event-stream')


@app.route('/claude/chat', methods=['POST'])
def claude_chat():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return Response("data: Error: ANTHROPIC_API_KEY not set\n\n", mimetype='text/event-stream')

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        data = request.get_json()
        messages = data.get('messages', [])

        def generate():
            with client.messages.stream(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                stream=True
            ) as stream:
                for text in stream.text_stream():
                    yield f"data: {text}\n\n"
            yield "data: [DONE]\n\n"

        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        return Response(f"data: Error: {str(e)}\n\n", mimetype='text/event-stream')


@app.route('/llama/chat', methods=['POST'])
def llama_chat():
    ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')

    try:
        data = request.get_json()
        messages = data.get('messages', [])
        model = data.get('model', 'llama3.1')

        req_data = {
            "model": model,
            "messages": messages,
            "stream": True
        }

        def generate():
            resp = requests.post(f"{ollama_url}/api/chat", json=req_data, stream=True)
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    content = chunk.get('message', {}).get('content', '')
                    if content:
                        yield f"data: {content}\n\n"
                    if chunk.get('done'):
                        break
            yield "data: [DONE]\n\n"

        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        return Response(f"data: Error: {str(e)}\n\n", mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
