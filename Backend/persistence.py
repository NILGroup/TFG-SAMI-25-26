import sqlite3
import re
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "persistence_SAMI.db"
#Inicializacion de la base de datos
def init_db():
    with sqlite3.connect(DB_PATH) as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS conversations(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                query TEXT NOT NULL,
                query_normalized TEXT NOT NULL,
                answer TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Indice para acelerar las consultas por user_id
        conexion.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_user_id
            ON conversations (user_id)
        """)
        # Indice para acelerar las consultas por category
        conexion.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_category
            ON conversations (category)
        """)
        conexion.commit()

#Normalizamos la query para mejorar la búsqueda de conversaciones anteriores
def normalize(query:str) -> str:
    query = query.lower().strip()
    query = re.sub(r'[¿?¡!.,;:"]', '', query)
    query = re.sub(r'\s+', ' ', query)
    return query

#Registramos la peticion del usuario
def log_conversation(user_id: str, category: str, query: str, answer: str):
    with sqlite3.connect(DB_PATH) as conexion:
        conexion.execute("""
            INSERT INTO conversations (user_id, category, query, query_normalized, answer, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, category, query.strip(), normalize(query), answer.strip(), datetime.now().isoformat()),)
        conexion.commit()

#Recogemos las 20 últimas interacciones del usuario
def get_history(user_id: str, category: str, limit: int = 20) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conexion:
        rows = conexion.execute("""
            SELECT query, answer, timestamp FROM conversations
            WHERE user_id = ? AND category = ?
            ORDER BY timestamp DESC LIMIT ?""",
            (user_id, category, limit)).fetchall()
    return [{"query": r[0], "answer": r[1], "timestamp": r[2]} for r in rows]

#Recogemos las 5 preguntas más frecuentes del usuario
def get_personal_faqs(user_id: str, category: str, limit: int = 5) -> list[str]:
    with sqlite3.connect(DB_PATH) as conexion:
        rows = conexion.execute("""
            SELECT query_normalized, COUNT(*) AS frequency,
            (SELECT query FROM conversations c2 WHERE c2.user_id = c1.user_id AND c2.category = c1.category AND c2.query_normalized = c1.query_normalized ORDER BY c2.timestamp DESC LIMIT 1) AS display_query
            FROM conversations c1
            WHERE user_id = ? AND category = ?
            GROUP BY query_normalized
            ORDER BY frequency DESC
            LIMIT ?""",
            (user_id, category, limit)).fetchall()
    return [r[2] for r in rows]

#Recogemos las 5 preguntas más frecuentes de todos los usuarios
def get_global_faqs(category: str, limit: int = 5) -> list[str]:
    with sqlite3.connect(DB_PATH) as conexion:
        rows = conexion.execute("""
            SELECT query_normalized, COUNT(*) AS frequency,
            (SELECT query FROM conversations c2 WHERE c2.query_normalized = c1.query_normalized AND c2.category = c1.category ORDER BY c2.timestamp DESC LIMIT 1) AS display_query
            FROM conversations c1
            WHERE category = ?
            GROUP BY query_normalized
            ORDER BY frequency DESC
            LIMIT ?""",
            (category, limit)).fetchall()
    return [r[2] for r in rows]