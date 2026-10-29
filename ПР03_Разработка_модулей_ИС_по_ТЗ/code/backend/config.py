import os
import secrets
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    DATABASE = os.environ.get('DATABASE') or os.path.join(
        BASE_DIR, 'database', 'conference.db')
    SCHEMA = os.path.join(BASE_DIR, 'schema.sql')

    SESSION_COOKIE_NAME = 'conf_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('COOKIE_SECURE') == '1'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    MAX_CONTENT_LENGTH = 64 * 1024

    ADMIN_LOGIN = 'Conf2027'
    ADMIN_PASSWORD = 'Demo77'

    LOGIN_MAX_ATTEMPTS = 5
    LOGIN_LOCK_SECONDS = 300


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-secret'
