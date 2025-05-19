from flask import Blueprint, render_template, request, redirect, url_for, flash
from urllib.parse import urlparse
import validators

from .models import find_url_by_name, insert_url, get_all_urls, get_url_by_id
from .logger import get_logger

routes = Blueprint('routes', __name__)
logger = get_logger(__name__)

@routes.route('/')
def index():
    logger.debug("Загружена стартовая страница")
    return render_template('index.html')

@routes.route('/urls', methods=['GET', 'POST'])
def urls():
    if request.method == 'POST':
        url = request.form.get('url')
        logger.info(f"Получен URL из формы: {url}")

        if not url or len(url) > 255 or not validators.url(url):
            flash('Некорректный URL', 'danger')
            logger.warning("Невалидный URL")
            return redirect(url_for('routes.index'))

        normalized_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
        existing = find_url_by_name(normalized_url)

        if existing:
            flash('Страница уже существует', 'info')
            return redirect(url_for('routes.url_detail', url_id=existing.id))

        try:
            url_id = insert_url(normalized_url)
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('routes.url_detail', url_id=url_id))
        except Exception:
            logger.exception("Ошибка при добавлении URL")
            flash('Что-то пошло не так', 'danger')
            return redirect(url_for('routes.index'))

    urls_list = get_all_urls()
    return render_template('urls.html', urls=urls_list)

@routes.route('/urls/<int:url_id>')
def url_detail(url_id):
    url_data = get_url_by_id(url_id)

    if not url_data:
        logger.error(f"URL с ID {url_id} не найден")
        flash('Ошибка: эта страница не должна была открыться', 'danger')
        return redirect(url_for('routes.urls'))

    return render_template(
        'url_detail.html',
        url_id=url_data.id,
        name=url_data.name,
        created_at=url_data.created_at
    )
