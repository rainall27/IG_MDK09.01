import os
import sqlite3

from werkzeug.security import generate_password_hash


class Database:
    _instance = None

    def __new__(cls, db_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_path = None
        if db_path:
            cls._instance.db_path = os.path.abspath(db_path)
        return cls._instance

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    def execute(self, query, params=()):
        conn = self.get_connection()
        try:
            cur = conn.execute(query, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def fetch_one(self, query, params=()):
        conn = self.get_connection()
        try:
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def fetch_all(self, query, params=()):
        conn = self.get_connection()
        try:
            return [dict(r) for r in conn.execute(query, params).fetchall()]
        finally:
            conn.close()

    def init_schema(self, schema_path):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(schema_path, encoding='utf-8') as f:
            script = f.read()
        conn = self.get_connection()
        try:
            conn.executescript(script)
            conn.commit()
        finally:
            conn.close()

    def seed_rooms(self, rooms):
        if self.fetch_one('SELECT id FROM room LIMIT 1'):
            return
        for name, capacity, description, image in rooms:
            self.execute('INSERT INTO room (name, capacity, description, image) VALUES (?, ?, ?, ?)',
                         (name, capacity, description, image))

    def ensure_admin(self, login, password):
        if self.fetch_one('SELECT id FROM user WHERE login = ?', (login,)):
            return
        self.execute(
            'INSERT INTO user (login, password_hash, fio, phone, email, role_id) '
            'VALUES (?, ?, ?, ?, ?, 2)',
            (login, generate_password_hash(password), 'Администратор портала',
             '8(800)000-00-00', 'admin@conf.rf'),
        )
