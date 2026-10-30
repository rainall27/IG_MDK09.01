from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from backend.app import create_app
from backend.database import Database

USERS = [
    ('ivanov01', 'Иванов Иван Иванович', '8(912)345-67-89', 'ivanov@mail.ru'),
    ('petrova22', 'Петрова Анна Сергеевна', '8(903)111-22-33', 'petrova@yandex.ru'),
    ('sidorov77', 'Сидоров Пётр Олегович', '8(925)555-44-11', 'sidorov@gmail.com'),
]


def main():
    create_app()
    db = Database()
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    for i, (login, fio, phone, email) in enumerate(USERS):
        if db.fetch_one('SELECT id FROM user WHERE login = ?', (login,)):
            continue
        uid = db.execute(
            'INSERT INTO user (login, password_hash, fio, phone, email, role_id) VALUES (?, ?, ?, ?, ?, 1)',
            (login, generate_password_hash('Password1'), fio, phone, email))
        for status, room, pay, days in ((1, 1 + i % 3, 1, 10 + i), (2, 1 + (i + 1) % 3, 2, 20 + i),
                                        (3, 1 + (i + 2) % 3, 2, -(7 + i))):
            start = (now + timedelta(days=days)).replace(hour=10 + i)
            rid = db.execute(
                'INSERT INTO request (user_id, room_id, payment_method_id, status_id, start_at, created_at) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (uid, room, pay, status, start.strftime('%Y-%m-%d %H:%M'),
                 min(now - timedelta(days=5 - status, hours=i),
                     start - timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')))
            if status == 3 and i == 0:
                db.execute('INSERT INTO review (request_id, text, rating) VALUES (?, ?, ?)',
                           (rid, 'Отличный зал, всё оборудование работало, организаторы помогли с регистрацией.', 5))
    print('Тестовые данные добавлены. Вход участника: ivanov01 / Password1, администратора: Conf2027 / Demo77')


if __name__ == '__main__':
    main()
