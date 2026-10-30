from functools import wraps

from flask import jsonify, redirect, request, session, url_for


def _wants_json():
    return request.path.startswith('/api/')


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            if _wants_json():
                return jsonify(error='Требуется авторизация'), 401
            return redirect(url_for('auth.login_page', next=request.path))
        return view(*args, **kwargs)
    return wrapper


def participant_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if session.get('role') != 'user':
            if _wants_json():
                return jsonify(error='Доступ только для участников'), 403
            return redirect(url_for('admin.admin_page'))
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            if _wants_json():
                return jsonify(error='Доступ запрещён'), 403
            return redirect(url_for('requests.dashboard'))
        return view(*args, **kwargs)
    return wrapper


def guest_only(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('admin.admin_page' if session.get('role') == 'admin'
                                    else 'requests.dashboard'))
        return view(*args, **kwargs)
    return wrapper
