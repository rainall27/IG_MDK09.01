import os

from flask import Flask, jsonify, render_template, request, session, url_for

from backend.config import BASE_DIR, Config
from backend.database import Database
from backend.routes.admin_routes import admin_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.main_routes import main_bp
from backend.routes.request_routes import request_bp
from backend.rooms import ROOMS
from backend.security.protection import LoginThrottle, csrf_protect, get_csrf_token, set_security_headers


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
        static_folder=os.path.join(BASE_DIR, 'frontend', 'static'),
    )
    app.config.from_object(config_class)

    db = Database(app.config['DATABASE'])
    db.init_schema(app.config['SCHEMA'])
    db.seed_rooms(ROOMS)
    db.ensure_admin(app.config['ADMIN_LOGIN'], app.config['ADMIN_PASSWORD'])

    app.extensions['login_throttle'] = LoginThrottle(
        app.config['LOGIN_MAX_ATTEMPTS'], app.config['LOGIN_LOCK_SECONDS'])

    for bp in (main_bp, auth_bp, request_bp, admin_bp):
        app.register_blueprint(bp)

    app.before_request(csrf_protect)
    app.after_request(set_security_headers)

    @app.context_processor
    def inject_globals():
        return {
            'csrf_token': get_csrf_token,
            'current_user': {'login': session.get('login'), 'fio': session.get('fio'),
                             'role': session.get('role')} if 'user_id' in session else None,
            'asset': lambda path: url_for('static', filename=path),
        }

    @app.errorhandler(404)
    def not_found(_e):
        if request.path.startswith('/api/'):
            return jsonify(error='Не найдено'), 404
        return render_template('error.html', code=404, text='Страница не найдена'), 404

    @app.errorhandler(400)
    def bad_request(_e):
        return render_template('error.html', code=400, text='Некорректный запрос'), 400

    @app.errorhandler(500)
    def server_error(_e):
        if request.path.startswith('/api/'):
            return jsonify(error='Внутренняя ошибка сервера'), 500
        return render_template('error.html', code=500, text='Внутренняя ошибка сервера'), 500

    return app
