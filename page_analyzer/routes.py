from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    make_response
)
from urllib.parse import urlparse
import validators
import requests

from .models import (
    find_url_by_name,
    insert_url,
    get_all_urls,
    get_url_by_id,
    get_check_data,
    check_url
)
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
        logger.info("Получен URL из формы: %s", url)

        if not url or len(url) > 255 or not validators.url(url):
            logger.warning("Невалидный URL")
            flash('Некорректный URL', 'danger')
            return make_response(render_template('index.html'), 422)

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
        logger.error("URL с ID %s не найден", url_id)
        flash('Ошибка: эта страница не должна была открыться', 'danger')
        return redirect(url_for('routes.urls'))
    checks = get_check_data(url_id)

    return render_template(
        'url_detail.html',
        url_id=url_data.id,
        name=url_data.name,
        created_at=url_data.created_at,
        checks=checks
    )


@routes.route('/urls/<int:url_id>/checks', methods=['POST'])
def urls_checks(url_id):
    try:
        check_url(url_id)
    except requests.exceptions.RequestException as e:
        logger.error("Страница не открывается url_id= %s, %s", url_id, e)
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for('routes.url_detail', url_id=url_id))
    
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('routes.url_detail', url_id=url_id))
