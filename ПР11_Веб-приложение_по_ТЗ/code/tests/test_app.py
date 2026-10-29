from datetime import datetime, timedelta

import pytest

from backend.app import create_app
from backend.config import TestConfig
from backend.database import Database


@pytest.fixture()
def app(tmp_path):
    class Cfg(TestConfig):
        DATABASE = str(tmp_path / 'test.db')
    Database._instance = None
    return create_app(Cfg)


@pytest.fixture()
def client(app):
    c = app.test_client()
    c.get('/')
    with c.session_transaction() as s:
        c.csrf = s['_csrf']
    return c


def post(client, url, data, method='post'):
    return getattr(client, method)(url, json=data, headers={'X-CSRF-Token': client.csrf})


USER = {'login': 'student01', 'password': 'Password1', 'fio': 'Иванов Иван Иванович',
        'phone': '8(912)345-67-89', 'email': 'student@mail.ru'}


def future(days=5):
    return (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%dT10:00')


def register_and_login(client, user=USER):
    post(client, '/api/register', user)
    r = post(client, '/api/login', {'login': user['login'], 'password': user['password']})
    with client.session_transaction() as s:
        s['_csrf'] = client.csrf
    return r

def test_register_ok(client):
    r = post(client, '/api/register', USER)
    assert r.status_code == 201


@pytest.mark.parametrize('field,value', [
    ('login', 'abc12'),
    ('login', 'логин123'),
    ('password', '1234567'),
    ('fio', 'Ivanov Ivan'),
    ('phone', '89123456789'),
    ('email', 'student@mail'),
])
def test_register_validation(client, field, value):
    r = post(client, '/api/register', {**USER, field: value})
    assert r.status_code == 422
    assert field in r.get_json()['errors']


def test_register_duplicate_login(client):
    post(client, '/api/register', USER)
    r = post(client, '/api/register', USER)
    assert r.get_json()['errors']['login'] == 'Такой логин уже занят'


def test_password_is_hashed(app, client):
    post(client, '/api/register', USER)
    row = Database().fetch_one('SELECT password_hash FROM user WHERE login = ?', (USER['login'],))
    assert row['password_hash'] != USER['password']
    assert row['password_hash'].startswith(('scrypt:', 'pbkdf2:'))

def test_login_wrong_password(client):
    post(client, '/api/register', USER)
    r = post(client, '/api/login', {'login': USER['login'], 'password': 'wrong-pass'})
    assert r.status_code == 401
    assert r.get_json()['errors']['form'] == 'Неверный логин или пароль'


def test_login_bruteforce_lock(client):
    post(client, '/api/register', USER)
    for _ in range(5):
        post(client, '/api/login', {'login': USER['login'], 'password': 'wrong-pass'})
    r = post(client, '/api/login', {'login': USER['login'], 'password': USER['password']})
    assert r.status_code == 429


def test_sql_injection_login(client):
    post(client, '/api/register', USER)
    r = post(client, '/api/login', {'login': "' OR '1'='1", 'password': "' OR '1'='1"})
    assert r.status_code == 401


def test_csrf_required(client):
    r = client.post('/api/register', json=USER)
    assert r.status_code == 400


def test_guest_cannot_open_dashboard(client):
    assert client.get('/dashboard').status_code == 302
    assert client.get('/api/requests').status_code == 401


def test_user_cannot_open_admin(client):
    register_and_login(client)
    assert client.get('/api/admin/requests').status_code == 403


def test_security_headers(client):
    r = client.get('/')
    assert r.headers['X-Frame-Options'] == 'DENY'
    assert 'Content-Security-Policy' in r.headers

def test_create_request_and_list(client):
    register_and_login(client)
    r = post(client, '/api/requests', {'room_id': 1, 'payment_method_id': 2, 'start_at': future()})
    assert r.status_code == 201
    items = client.get('/api/requests').get_json()['requests']
    assert len(items) == 1 and items[0]['status'] == 'Новая'


def test_create_request_past_date(client):
    register_and_login(client)
    past = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT10:00')
    r = post(client, '/api/requests', {'room_id': 1, 'payment_method_id': 1, 'start_at': past})
    assert r.get_json()['errors']['start_at'] == 'Дата начала должна быть в будущем'


def test_create_request_empty(client):
    register_and_login(client)
    errors = post(client, '/api/requests', {}).get_json()['errors']
    assert set(errors) == {'room_id', 'payment_method_id', 'start_at'}

def login_admin(client):
    r = post(client, '/api/login', {'login': 'Conf2027', 'password': 'Demo77'})
    with client.session_transaction() as s:
        s['_csrf'] = client.csrf
    return r


def test_full_cycle_review_after_done(app):
    user = app.test_client(); user.get('/')
    with user.session_transaction() as s:
        user.csrf = s['_csrf']
    register_and_login(user)
    req_id = post(user, '/api/requests', {'room_id': 2, 'payment_method_id': 1,
                                          'start_at': future()}).get_json()['id']

    r = post(user, f'/api/requests/{req_id}/review', {'rating': 5, 'text': 'Отличное мероприятие!'})
    assert r.status_code == 409

    admin = app.test_client(); admin.get('/')
    with admin.session_transaction() as s:
        admin.csrf = s['_csrf']
    assert login_admin(admin).status_code == 200
    assert post(admin, f'/api/admin/requests/{req_id}/status', {'status_id': 2}, 'patch').status_code == 200
    assert post(admin, f'/api/admin/requests/{req_id}/status', {'status_id': 2}, 'patch').status_code == 400
    assert post(admin, f'/api/admin/requests/{req_id}/status', {'status_id': 3}, 'patch').status_code == 200

    r = post(user, f'/api/requests/{req_id}/review', {'rating': 5, 'text': 'Отличное мероприятие!'})
    assert r.status_code == 201
    r = post(user, f'/api/requests/{req_id}/review', {'rating': 4, 'text': 'Ещё один отзыв тут'})
    assert r.status_code == 409


def test_admin_filters(app, client):
    register_and_login(client)
    post(client, '/api/requests', {'room_id': 1, 'payment_method_id': 1, 'start_at': future()})
    post(client, '/api/requests', {'room_id': 3, 'payment_method_id': 2, 'start_at': future(9)})
    admin = app.test_client(); admin.get('/')
    with admin.session_transaction() as s:
        admin.csrf = s['_csrf']
    login_admin(admin)
    assert len(admin.get('/api/admin/requests').get_json()['requests']) == 2
    assert len(admin.get('/api/admin/requests?room=3').get_json()['requests']) == 1
    assert len(admin.get('/api/admin/requests?status=2').get_json()['requests']) == 0
    assert len(admin.get('/api/admin/requests?q=Иванов').get_json()['requests']) == 2


def test_profile_page(client):
    assert client.get('/profile').status_code == 302
    register_and_login(client)
    post(client, '/api/requests', {'room_id': 1, 'payment_method_id': 1, 'start_at': future()})
    html = client.get('/profile').get_data(as_text=True)
    assert 'Личный кабинет' in html and USER['login'] in html and USER['phone'] in html
