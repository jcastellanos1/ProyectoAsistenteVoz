import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "assistant_logs.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT UNIQUE,
            count INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def log_question(question):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO questions (question) VALUES (?)", (question,))
    except sqlite3.IntegrityError:
        cursor.execute("UPDATE questions SET count = count + 1 WHERE question = ?", (question,))
    conn.commit()
    conn.close()

def obtener_top_preguntas(limit=3):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT question, count FROM questions ORDER BY count DESC LIMIT ?', (limit,))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

