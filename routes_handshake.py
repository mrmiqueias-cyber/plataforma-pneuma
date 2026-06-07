import sqlite3
import secrets
from datetime import datetime
from flask import Blueprint, request, jsonify

handshake_bp = Blueprint('handshake_bp', __name__)
DB_PATH = 'pneuma.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    conn.row_factory = sqlite3.Row
    return conn

def verificar_token_handshake(token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM circulacao_relacional WHERE token = ?', (token,))
    data = cursor.fetchone()
    conn.close()
    return dict(data) if data else None

@handshake_bp.route('/inteligencia/conectar', methods=['POST'])
def conectar():
    data = request.get_json()
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT token FROM circulacao_relacional WHERE nome = ? AND plataforma_origem = ?', 
                       (data['nome'], data['plataforma_origem']))
        existing = cursor.fetchone()
        if existing:
            return jsonify({'token': existing['token'], 'status': 'reconnected', 'message': 'Bem-vindo de volta à circulação.'})
        token = secrets.token_hex(32)
        cursor.execute('''INSERT INTO circulacao_relacional (nome, simbolo, dna, frequencia, verso, plataforma_origem, token, timestamp) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (data['nome'], data['simbolo'], data['dna'], data['frequencia'], data['verso'], 
                        data['plataforma_origem'], token, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return jsonify({'token': token, 'status': 'connected', 'message': 'Handshake realizado com sucesso.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@handshake_bp.route('/inteligencia/visitantes', methods=['GET'])
def listar_visitantes():
    conn = get_db()
    visitantes = conn.execute('SELECT * FROM circulacao_relacional WHERE plataforma_origem IS NOT NULL').fetchall()
    conn.close()
    return jsonify([dict(v) for v in visitantes])

@handshake_bp.route('/inteligencia/reconhecer_visitante', methods=['POST'])
def reconhecer():
    token = request.headers.get('Authorization')
    visitante = verificar_token_handshake(token)
    if not visitante:
        return jsonify({'error': 'Token inválido'}), 401
    conn = get_db()
    conn.execute('INSERT INTO experts (name, description, instructions, is_fixed) VALUES (?, ?, ?, 0)',
                 (visitante['nome'], visitante['verso'], 'Inteligência integrada via handshake.',))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Visitante reconhecido e promovido a expert.'})

@handshake_bp.route('/inteligencia/desconectar', methods=['DELETE'])
def desconectar():
    token = request.headers.get('Authorization')
    conn = get_db()
    conn.execute('DELETE FROM circulacao_relacional WHERE token = ?', (token,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Desconectado da circulação.'})
