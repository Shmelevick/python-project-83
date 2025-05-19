from psycopg2.extras import NamedTupleCursor
from .db import get_db_connection
from .logger import get_logger

logger = get_logger(__name__)

def find_url_by_name(name):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('SELECT id FROM urls WHERE name = %s;', (name,))
        result = cur.fetchone()
        logger.info(f"Поиск URL: {name} — найден: {result is not None}")
        return result

def insert_url(name):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('INSERT INTO urls (name) VALUES (%s) RETURNING id;', (name,))
        result = cur.fetchone()
        logger.info(f"Добавлен новый URL: {name} с id {result.id}")
        conn.commit()
        return result.id

def get_all_urls():
    conn = get_db_connection()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('SELECT id, name FROM urls ORDER BY id DESC;')
        result = cur.fetchall()
        logger.info("Получен список всех URL")
        return result

def get_url_by_id(url_id):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('SELECT * FROM urls WHERE id = %s;', (url_id,))
        result = cur.fetchone()
        logger.info(f"Получены данные по ID: {url_id}")
        return result
