from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for

from backend.models.user import User
from backend.security.decorators import guest_only

auth_bp = Blueprint('auth', __name__)


@auth_bp.get('/register')
@guest_only
def register_page():
    return render_template('register.html')


@auth_bp.get('/login')
@guest_only
def login_page():
    return render_template('login.html')


@auth_bp.post('/api/register')
def api_register():
    data = request.get_json(silent=True) or {}
    user, errors = User.register(
        login=str(data.get('login', '')).strip(),
        password=str(data.get('password', '')),
        fio=str(data.get('fio', '')),
        phone=str(data.get('phone', '')).strip(),
        email=str(data.get('email', '')).strip(),
    )
    if errors:
        return jsonify(errors=errors), 422
    return jsonify(message='Пользователь создан. Теперь войдите в систему.',
                   redirect=url_for('auth.login_page')), 201


@auth_bp.post('/api/login')
def api_login():
    data = request.get_json(silent=True) or {}
    login = str(data.get('login', '')).strip()
    password = str(data.get('password', ''))

    errors = {}
    if not login:
        errors['login'] = 'Введите логин'
    if not password:
        errors['password'] = 'Введите пароль'
    if errors:
        return jsonify(errors=errors), 422

    throttle = current_app.extensions['login_throttle']
    wait = throttle.is_locked(login)
    if wait:
        return jsonify(errors={'form': f'Слишком много попыток. Повторите через {wait} с.'}), 429

    user = User.authenticate(login, password)
    if not user:
        throttle.fail(login)
        return jsonify(errors={'form': 'Неверный логин или пароль'}), 401

    throttle.reset(login)
    session.clear()
    session.permanent = True
    session['user_id'] = user.id
    session['login'] = user.login
    session['fio'] = user.fio
    session['role'] = 'admin' if user.is_admin else 'user'
    target = url_for('admin.admin_page') if user.is_admin else url_for('requests.dashboard')
    return jsonify(message='Вход выполнен', redirect=target)


@auth_bp.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))
