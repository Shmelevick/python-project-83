import requests
from bs4 import BeautifulSoup

from psycopg2.extras import NamedTupleCursor
from .db import get_db_connection
from .logger import get_logger

logger = get_logger(__name__)

def find_url_by_name(name):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute('SELECT id FROM urls WHERE name = %s;', (name,))
        result = cur.fetchone()
        logger.info("Поиск URL: %s — найден: %s", name, result is not None)
        return result

def insert_url(name):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        query = 'INSERT INTO urls (name) VALUES (%s) RETURNING id;'
        cur.execute(query, (name,))
        result = cur.fetchone()
        logger.info("Добавлен новый URL: %s с id %s", name, result.id)
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
        logger.info("Получены данные по ID %s: %s", url_id, result)
        return result

def get_check_data(url_id):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute(
            'SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC;',
            (url_id,)
        )
        result = cur.fetchall()
        logger.info('Получены данные из url_checks по url_id: %s', url_id)
        return result

def insert_check(url_id):
    conn = get_db_connection()
    url = get_url_by_id(url_id)
    response = requests.get(url.name)
    response.raise_for_status()
    status_code = response.status_code

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else ''
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description = (
        description_tag['content'] 
        if description_tag and 'content' in description_tag.attrs
        else ''
    )
    h1_tag = soup.find('h1')
    h1 = h1_tag.text.strip() if h1_tag else ''

    with conn.cursor() as cur:
        query = """
        INSERT INTO url_checks (url_id, h1, status_code, title, description)
        VALUES (%s, %s, %s, %s, %s);
        """
        cur.execute(query, (url_id, h1, status_code, title, description))
        conn.commit()
        logger.info("Вставлены данные о проверке url_id = %s", url_id)
