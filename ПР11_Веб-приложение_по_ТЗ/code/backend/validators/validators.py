import re
from datetime import datetime

LOGIN_RE = re.compile(r'^[A-Za-z0-9]{6,50}$')
FIO_RE = re.compile(r'^[А-Яа-яЁё]+(?: [А-Яа-яЁё]+)*$')
PHONE_RE = re.compile(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$')
EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')


class Validator:

    @staticmethod
    def login(value):
        if not value:
            return 'Введите логин'
        if not LOGIN_RE.match(value):
            return 'Логин: только латиница и цифры, не менее 6 символов'
        return ''

    @staticmethod
    def password(value):
        if not value:
            return 'Введите пароль'
        if len(value) < 8:
            return 'Пароль должен быть не короче 8 символов'
        if len(value) > 128:
            return 'Пароль слишком длинный'
        return ''

    @staticmethod
    def fio(value):
        value = (value or '').strip()
        if not value:
            return 'Введите ФИО'
        if len(value) > 150 or not FIO_RE.match(value):
            return 'ФИО: только кириллица и пробелы'
        return ''

    @staticmethod
    def phone(value):
        if not value:
            return 'Введите телефон'
        if not PHONE_RE.match(value):
            return 'Телефон в формате 8(XXX)XXX-XX-XX'
        return ''

    @staticmethod
    def email(value):
        if not value:
            return 'Введите email'
        if len(value) > 100 or not EMAIL_RE.match(value):
            return 'Некорректный адрес электронной почты'
        return ''

    @staticmethod
    def start_at(value):
        if not value:
            return 'Укажите дату и время начала конференции', None
        try:
            dt = datetime.strptime(value, '%Y-%m-%dT%H:%M')
        except ValueError:
            return 'Некорректная дата и время', None
        if dt <= datetime.now():
            return 'Дата начала должна быть в будущем', None
        return '', dt

    @staticmethod
    def rating(value):
        try:
            v = int(value)
        except (TypeError, ValueError):
            return 'Поставьте оценку от 1 до 5'
        return '' if 1 <= v <= 5 else 'Поставьте оценку от 1 до 5'

    @staticmethod
    def review_text(value):
        value = (value or '').strip()
        if len(value) < 10:
            return 'Отзыв должен быть не короче 10 символов'
        if len(value) > 1000:
            return 'Отзыв не длиннее 1000 символов'
        return ''
