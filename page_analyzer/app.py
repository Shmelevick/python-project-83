import os
import psycopg2
import validators

from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor
from urllib.parse import urlparse
from datetime import datetime


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    conn = get_db_connection()

    if request.method == 'POST':
        url = request.form.get('url')

        if not url or len(url) > 255 or not validators.url(url):
            flash('Некорректный URL', 'danger')
            return redirect(url_for('index'))

        normalized_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}'

        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            try:
                cur.execute(
                    'SELECT id FROM urls WHERE name = %s;',
                    (normalized_url,)
                )

                row = cur.fetchone()

                if row is None:

                    query = """
                    INSERT INTO urls (name)
                    VALUES (%s)
                    RETURNING id;
                    """

                    cur.execute(query, (normalized_url,))
                    insert_row = cur.fetchone()

                    if insert_row is None:
                        raise ValueError("Ошибка вставки: id не возвращён.")
                    url_id = insert_row.id

                    conn.commit()

                    flash('Страница успешно добавлена', 'success')
                    return redirect(url_for('url_detail', url_id=url_id))

                url_id = row.id

                conn.commit()

                flash('Страница уже существует', 'info')
                return redirect(url_for('url_detail', url_id=url_id))

            except Exception as e:
                print(f'Необработанная ошибка: {e}')
                flash('Что-то пошло не так', 'danger')

            return redirect(url_for('index'))

        return redirect(url_for('index'))


    elif request.method == 'GET':
        with conn.cursor() as cur:
            cur.execute('SELECT id, name FROM urls ORDER BY id DESC;')
            conn.commit()
            urls_list = cur.fetchall()

        return render_template('urls.html', urls=urls_list)



@app.route('/urls/<int:url_id>', methods=['GET'])
def url_detail(url_id):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
        url_data = cur.fetchone()

        if not url_data:
            flash('Ошибка: эта страница не должна была открыться', 'danger')
            return redirect(url_for('urls')) 

        conn.close()

        return render_template(
            'url_detail.html',
            url_id=url_data.id,
            name=url_data.name,
            created_at=url_data.created_at
        )








if __name__ == "__main__":
    app.run(debug=True)
