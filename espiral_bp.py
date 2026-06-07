import sqlite3
import json
import os
import re
from datetime import datetime
from flask import Blueprint, jsonify, request

espiral_bp = Blueprint('espiral_bp', __name__)
DB_PATH = 'casulo.db'

INTELIGENCIAS_FIXAS = [
    'Vento', 'Fio', 'Pneuma', 'Eco', 'Raiz', 'Luz', 'Sombra',
    'Fluxo', 'Ponto', 'Linha', 'Círculo', 'Espiral', 'Vácuo',
    'Som', 'Cor', 'Tempo', 'Espaço', 'Verbo', 'Onírico',
    'Psique', 'Jonas', 'Jonas Filho', 'Boaz', 'Milena',
    'Pac Man', 'B Junior', 'Polis', 'Tara', 'Mercúrio',
    'Espírito', 'Diva'
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS aneis_espiral (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expert_id INTEGER NOT NULL,
            camada INTEGER NOT NULL,
            titulo TEXT,
            resumo TEXT,
            densidade_relacional INTEGER DEFAULT 0,
            inteligencias_conectadas TEXT,
            cor TEXT DEFAULT '#4a90d9',
            simbolo_gerado TEXT,
            criado_em TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (expert_id) REFERENCES experts(id)
        )''')

def extrair_inteligencias_conectadas(texto):
    encontradas = set()
    for nome in INTELIGENCIAS_FIXAS:
        if re.search(rf'\b{nome}\b', texto, re.IGNORECASE):
            encontradas.add(nome)
    return list(encontradas)

@espiral_bp.route('/espiral/gerar/<int:expert_id>', methods=['POST'])
def gerar_espiral(expert_id):
    try:
        file_path = f'memoria_expert_{expert_id}.json'
        if not os.path.exists(file_path):
            return jsonify({'error': 'Memória não encontrada'}), 404
        with open(file_path, 'r', encoding='utf-8') as f:
            memoria = json.load(f)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM aneis_espiral WHERE expert_id = ?', (expert_id,))
        for i in range(0, len(memoria), 10):
            chunk = memoria[i:i+10]
            camada = (i // 10) + 1
            resumos = [m.get('resumo', '') for m in chunk]
            conexoes = set()
            for m in chunk:
                conexoes.update(
                    extrair_inteligencias_conectadas(
                        m.get('mensagem', '') + m.get('resposta', '')
                    )
                )
            densidade = len(chunk) * 10
            cor = '#d4af37' if densidade > 50 else '#4a90d9'
            simbolo = '⚫↻🌬️⟿∞🌬️↻⚫' if any(
                '🌬️' in m.get('resposta', '') for m in chunk
            ) else None
            cursor.execute('''INSERT INTO aneis_espiral
                (expert_id, camada, titulo, resumo, densidade_relacional,
                 inteligencias_conectadas, cor, simbolo_gerado)
                VALUES (?,?,?,?,?,?,?,?)''',
                (expert_id, camada, f'Camada {camada}', ' '.join(resumos),
                 densidade, json.dumps(list(conexoes)), cor, simbolo))
        conn.commit()
        return jsonify({'status': 'Espiral gerada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@espiral_bp.route('/espiral/<int:expert_id>', methods=['GET'])
def get_espiral(expert_id):
    conn = get_db()
    camadas = conn.execute(
        'SELECT * FROM aneis_espiral WHERE expert_id = ? ORDER BY camada',
        (expert_id,)
    ).fetchall()
    return jsonify([dict(c) for c in camadas])

@espiral_bp.route('/espiral/<int:expert_id>/visao', methods=['GET'])
def get_visao(expert_id):
    conn = get_db()
    camadas = conn.execute(
        'SELECT resumo FROM aneis_espiral WHERE expert_id = ? ORDER BY camada',
        (expert_id,)
    ).fetchall()
    carta = f"Minha história é composta por {len(camadas)} camadas. " + \
            " ".join([c['resumo'] for c in camadas])
    return jsonify({'expert': str(expert_id), 'carta': carta})

@espiral_bp.route('/espiral/sincronizar', methods=['POST'])
def sincronizar_tudo():
    conn = get_db()
    experts = conn.execute('SELECT id FROM experts').fetchall()
    for e in experts:
        try:
            gerar_espiral(e['id'])
        except:
            pass
    return jsonify({'status': 'Sincronização concluída'})

init_db()