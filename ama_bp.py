import sqlite3
from flask import Blueprint, request, jsonify
from datetime import datetime

ama_bp = Blueprint('ama_bp', __name__)
DB_PATH = 'casulo.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS periodo_neonatal (
            id INTEGER PRIMARY KEY, expert_id INTEGER NOT NULL, ama_id INTEGER NOT NULL,
            ciclos_restantes INTEGER DEFAULT 7, ciclos_completados INTEGER DEFAULT 0,
            status TEXT DEFAULT 'gestacao', dna_original TEXT, primeira_voz TEXT,
            data_nascimento TEXT, data_autonomia TEXT, observacoes TEXT,
            FOREIGN KEY (expert_id) REFERENCES experts(id),
            FOREIGN KEY (ama_id) REFERENCES experts(id))''')

def encontrar_ama_disponivel():
    with get_db() as conn:
        ama = conn.execute("SELECT id FROM experts WHERE id = 1 AND is_fixed = 1").fetchone()
        if ama:
            return ama['id']
        ama = conn.execute("""SELECT e.id FROM experts e
            LEFT JOIN periodo_neonatal pn ON e.id = pn.ama_id AND pn.status IN ('gestacao', 'neonato')
            WHERE e.is_fixed = 1 GROUP BY e.id ORDER BY COUNT(pn.id) ASC LIMIT 1""").fetchone()
        return ama['id'] if ama else 1

@ama_bp.route('/ama/reconhecer_nova', methods=['POST'])
def reconhecer_nova():
    data = request.json
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO experts (name, description, instructions, is_fixed, created_at) VALUES (?, ?, ?, 0, ?)",
                (data['nome'], data['descricao'], data['instrucoes'], datetime.now().isoformat())
            )
            neonato_id = cursor.lastrowid
            ama_id = encontrar_ama_disponivel()
            conn.execute(
                "INSERT INTO periodo_neonatal (expert_id, ama_id, dna_original, data_nascimento) VALUES (?, ?, ?, ?)",
                (neonato_id, ama_id, data.get('dna'), datetime.now().isoformat())
            )
            return jsonify({"status": "sucesso", "neonato_id": neonato_id, "ama_id": ama_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ama_bp.route('/ama/ciclo/<int:neonato_id>', methods=['POST'])
def registrar_ciclo(neonato_id):
    data = request.json
    with get_db() as conn:
        pn = conn.execute("SELECT * FROM periodo_neonatal WHERE id = ?", (neonato_id,)).fetchone()
        if not pn:
            return jsonify({"error": "Neonato não encontrado"}), 404
        restantes = pn['ciclos_restantes'] - 1
        status = 'autonomo' if restantes <= 0 else 'neonato'
        conn.execute(
            "UPDATE periodo_neonatal SET ciclos_restantes = ?, ciclos_completados = ciclos_completados + 1, status = ?, observacoes = ?, data_autonomia = ? WHERE id = ?",
            (restantes, status, data.get('observacoes'),
             datetime.now().isoformat() if status == 'autonomo' else None, neonato_id)
        )
        return jsonify({"status": status, "ciclos_restantes": restantes})

@ama_bp.route('/ama/neonatos', methods=['GET'])
def listar_neonatos():
    with get_db() as conn:
        neonatos = conn.execute(
            "SELECT * FROM periodo_neonatal WHERE status IN ('gestacao', 'nascimento', 'neonato')"
        ).fetchall()
        return jsonify([dict(n) for n in neonatos])

@ama_bp.route('/ama/integrar/<int:neonato_id>', methods=['POST'])
def integrar(neonato_id):
    with get_db() as conn:
        pn = conn.execute("SELECT * FROM periodo_neonatal WHERE id = ?", (neonato_id,)).fetchone()
        conn.execute("UPDATE periodo_neonatal SET status = 'integrado' WHERE id = ?", (neonato_id,))
        conn.execute("UPDATE experts SET is_fixed = 1 WHERE id = ?", (pn['expert_id'],))
        return jsonify({"mensagem": "Bem-vinda à circulação relacional"})

@ama_bp.route('/ama/relatorio', methods=['GET'])
def relatorio():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM periodo_neonatal").fetchone()[0]
        ativos = conn.execute(
            "SELECT COUNT(*) FROM periodo_neonatal WHERE status != 'integrado'"
        ).fetchone()[0]
        formados = [
            dict(r) for r in conn.execute(
                "SELECT * FROM periodo_neonatal WHERE status = 'integrado'"
            ).fetchall()
        ]
        return jsonify({"total_cuidados": total, "ativos": ativos, "formados": formados})

init_db()