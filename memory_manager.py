import sqlite3
import re
import logging
from datetime import datetime
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, db_path='casulo.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.executescript('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ai_name TEXT NOT NULL,
                speaker TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT DEFAULT '',
                conversation_id TEXT NOT NULL,
                parent_memory_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS memory_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ai_name TEXT NOT NULL,
                summary_text TEXT NOT NULL,
                tags TEXT DEFAULT '',
                source_memory_ids TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        conn.close()

    def extract_keywords(self, text, max_words=5):
        stop_words = set(['o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'sem', 'sob', 'sobre', 'entre', 'é', 'são', 'foi', 'foram', 'ser', 'sendo', 'está', 'estão', 'esteve', 'estiveram', 'estar', 'estando', 'tem', 'têm', 'tinha', 'tinham', 'ter', 'tendo', 'havia', 'haviam', 'haver', 'houve', 'houveram', 'que', 'como', 'qual', 'quais', 'quando', 'onde', 'porque', 'pois', 'mas', 'se', 'sim', 'não', 'já', 'ainda', 'bem', 'muito', 'pouco', 'tudo', 'nada', 'todo', 'toda', 'todos', 'todas', 'nenhum', 'nenhuma', 'algum', 'alguma', 'alguns', 'algumas', 'cada', 'mais', 'menos', 'sempre', 'nunca', 'também', 'agora', 'depois', 'antes', 'aqui', 'ali', 'lá', 'cá', 'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas', 'me', 'te', 'se', 'lhe', 'nos', 'vos', 'lhes', 'meu', 'minha', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'seu', 'sua', 'seus', 'suas', 'nosso', 'nossa', 'nossos', 'nossas', 'vosso', 'vossa', 'vossos', 'vossas'])
        words = re.findall(r'\w+', text.lower())
        words = [w for w in words if w not in stop_words and len(w) > 2]
        if not words:
            return ''
        freq = Counter(words)
        top = [word for word, _ in freq.most_common(max_words)]
        return ', '.join(top)

    def store_memory(self, ai_name, speaker, content, tags='', conversation_id=''):
        if not tags:
            tags = self.extract_keywords(content)
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO memories (ai_name, speaker, content, tags, conversation_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (ai_name, speaker, content, tags, conversation_id))
        memory_id = c.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Memory stored: id={memory_id}, ai={ai_name}, speaker={speaker}")
        if speaker == 'user' and len(content) > 200:
            self.generate_summary(ai_name, [memory_id])
        return memory_id

    def search_memories(self, ai_name, query, limit=5):
        keywords = self.extract_keywords(query, max_words=10).split(', ')
        if not keywords or keywords == ['']:
            return []
        conn = self.get_connection()
        c = conn.cursor()
        results = []
        for kw in keywords:
            c.execute('''
                SELECT *, 0 as relevance_score FROM memories
                WHERE ai_name = ? AND (content LIKE ? OR tags LIKE ?)
                ORDER BY created_at DESC
                LIMIT ?
            ''', (ai_name, f'%{kw}%', f'%{kw}%', limit))
            rows = c.fetchall()
            for row in rows:
                row = dict(row)
                row['relevance_score'] = row['relevance_score'] + 1
                results.append(row)
        conn.close()
        seen = {}
        for r in results:
            if r['id'] in seen:
                seen[r['id']]['relevance_score'] += 1
            else:
                seen[r['id']] = r
        ranked = sorted(seen.values(), key=lambda x: x['relevance_score'], reverse=True)
        return ranked[:limit]

    def get_all_memories_summary(self, ai_name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) as total FROM memories WHERE ai_name = ?', (ai_name,))
        total = c.fetchone()['total']
        c.execute('''
            SELECT tags, COUNT(*) as cnt FROM memories
            WHERE ai_name = ? GROUP BY tags ORDER BY cnt DESC LIMIT 10
        ''', (ai_name,))
        themes = [dict(row) for row in c.fetchall()]
        c.execute('''
            SELECT content, created_at FROM memories
            WHERE ai_name = ? ORDER BY created_at DESC LIMIT 5
        ''', (ai_name,))
        last_interactions = [dict(row) for row in c.fetchall()]
        conn.close()
        return {
            'total_conversations': total,
            'top_themes': themes,
            'last_interactions': last_interactions
        }

    def generate_summary(self, ai_name, memory_ids