import os
from flask import Flask, flash, render_template, request, redirect, url_for
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse
import validators
from page_analyzer.models import url_model
from page_analyzer.models import check_model
import requests
from bs4 import BeautifulSoup


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def normalize_url(url):
    parsed_url = urlparse(url)
    normalized_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
    return normalized_url


def is_valid(url):
    if not url:
        return 'URL не должен быть пустым'
    if len(url) > 255:
        return 'URL не должен превышать 255 символов'
    if not validators.url(url):
        return 'Некорректный URL'
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=["POST"])
def urls_post():
    url = request.form.get('url', '').strip()
    errors = is_valid(url)
    if errors:
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            url=url,
            errors=errors,
        ), 422  
    normalized_url = normalize_url(url)
    if url_model.url_exists(normalized_url):
        flash('Страница уже существует', 'warning')
        existing_url = url_model.get_url_by_name(normalized_url)
        if existing_url:
            return redirect(url_for('show_url', id=existing_url['id']))
    url_id = url_model.add_url_to_db(normalized_url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', id=url_id))


@app.route('/urls')
def list_urls():
    urls = url_model.get_all_urls()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>')
def show_url(id):
    url = url_model.get_url_by_id(id)
    if not url:
        flash('Страница не найдена', 'danger')
        return redirect(url_for('list_urls'))
    checks = check_model.get_checks_by_url_id(id)
    return render_template('url.html', url=url, checks=checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def run_check(id):
    url = url_model.get_url_by_id(id)
    if not url:
        flash('Страница не найдена', 'danger')
        return redirect(url_for('list_urls'))
    try:
        response = requests.get(url[1], timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        h1_tag = soup.find('h1')
        h1 = h1_tag.get_text(strip=True) if h1_tag else ''
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        description = meta_tag.get('content', '').strip() if meta_tag else ''
        check_model.add_check_full(id, response.status_code, h1, title, description)
        flash('Страница успешно проверена', 'success')

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
    
    return redirect(url_for('show_url', id=id))

