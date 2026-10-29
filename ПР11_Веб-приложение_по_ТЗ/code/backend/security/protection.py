import hmac
import secrets
import time

from flask import abort, jsonify, request, session

def get_csrf_token():
    if '_csrf' not in session:
        session['_csrf'] = secrets.token_urlsafe(32)
    return session['_csrf']


def csrf_protect():
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return None
    sent = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token', '')
    expected = session.get('_csrf', '')
    if not expected or not hmac.compare_digest(sent, expected):
        if request.path.startswith('/api/'):
            return jsonify(error='Сессия устарела, обновите страницу'), 400
        abort(400)
    return None

class LoginThrottle:

    def __init__(self, max_attempts, lock_seconds):
        self.max_attempts = max_attempts
        self.lock_seconds = lock_seconds
        self._fails = {}

    def is_locked(self, login):
        count, since = self._fails.get(login.lower(), (0, 0))
        if count >= self.max_attempts and time.time() - since < self.lock_seconds:
            return int(self.lock_seconds - (time.time() - since))
        if count >= self.max_attempts:
            self._fails.pop(login.lower(), None)
        return 0

    def fail(self, login):
        count, since = self._fails.get(login.lower(), (0, time.time()))
        self._fails[login.lower()] = (count + 1, since)

    def reset(self, login):
        self._fails.pop(login.lower(), None)

def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; "
        "script-src 'self'; font-src 'self'; frame-ancestors 'none'; form-action 'self'"
    )
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response
