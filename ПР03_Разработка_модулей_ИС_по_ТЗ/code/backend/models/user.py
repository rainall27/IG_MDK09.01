from werkzeug.security import check_password_hash, generate_password_hash

from backend.models.base_model import BaseModel
from backend.validators.validators import Validator


class User(BaseModel):
    table = 'user'

    ROLE_USER = 1
    ROLE_ADMIN = 2

    @property
    def is_admin(self):
        return getattr(self, 'role_id', None) == self.ROLE_ADMIN

    def validate(self, password=''):
        errors = {
            'login': Validator.login(getattr(self, 'login', '')),
            'password': Validator.password(password),
            'fio': Validator.fio(getattr(self, 'fio', '')),
            'phone': Validator.phone(getattr(self, 'phone', '')),
            'email': Validator.email(getattr(self, 'email', '')),
        }
        errors = {k: v for k, v in errors.items() if v}
        if 'login' not in errors and User.find_by_login(self.login):
            errors['login'] = 'Такой логин уже занят'
        return errors

    @classmethod
    def find_by_login(cls, login):
        row = cls.db().fetch_one('SELECT * FROM user WHERE login = ?', (login,))
        return cls(**row) if row else None

    @classmethod
    def register(cls, login, password, fio, phone, email):
        user = cls(login=login, fio=(fio or '').strip(), phone=phone, email=email)
        errors = user.validate(password)
        if errors:
            return None, errors
        user.password_hash = generate_password_hash(password)
        user.id = cls.db().execute(
            'INSERT INTO user (login, password_hash, fio, phone, email, role_id) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (user.login, user.password_hash, user.fio, user.phone, user.email, cls.ROLE_USER),
        )
        user.role_id = cls.ROLE_USER
        return user, {}

    @classmethod
    def authenticate(cls, login, password):
        user = cls.find_by_login(login or '')
        if user and check_password_hash(user.password_hash, password or ''):
            return user
        return None
