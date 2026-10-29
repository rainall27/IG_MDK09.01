from backend.models.base_model import BaseModel
from backend.models.reference import PaymentMethod, Room, Status
from backend.validators.validators import Validator

_SELECT = '''
    SELECT r.id, r.start_at, r.created_at, r.status_id,
           r.room_id, rm.name AS room, rm.image AS room_image,
           r.payment_method_id, pm.name AS payment_method,
           s.name AS status,
           u.id AS user_id, u.login, u.fio, u.phone, u.email,
           rv.id AS review_id, rv.text AS review_text, rv.rating AS review_rating
    FROM request r
    JOIN room rm           ON rm.id = r.room_id
    JOIN payment_method pm ON pm.id = r.payment_method_id
    JOIN status s          ON s.id = r.status_id
    JOIN user u            ON u.id = r.user_id
    LEFT JOIN review rv    ON rv.request_id = r.id
'''


class Request(BaseModel):
    table = 'request'

    def validate(self):
        errors = {}
        if not Room.get_by_id(getattr(self, 'room_id', None)):
            errors['room_id'] = 'Выберите помещение'
        if not PaymentMethod.get_by_id(getattr(self, 'payment_method_id', None)):
            errors['payment_method_id'] = 'Выберите способ оплаты'
        err, dt = Validator.start_at(getattr(self, 'start_at', ''))
        if err:
            errors['start_at'] = err
        else:
            self.start_at = dt.strftime('%Y-%m-%d %H:%M')
        return errors

    @classmethod
    def create(cls, user_id, room_id, payment_method_id, start_at):
        req = cls(user_id=user_id, room_id=_to_int(room_id),
                  payment_method_id=_to_int(payment_method_id), start_at=start_at)
        errors = req.validate()
        if errors:
            return None, errors
        req.id = cls.db().execute(
            'INSERT INTO request (user_id, room_id, payment_method_id, start_at, status_id) '
            'VALUES (?, ?, ?, ?, ?)',
            (user_id, req.room_id, req.payment_method_id, req.start_at, Status.NEW),
        )
        return req, {}

    @classmethod
    def list_for_user(cls, user_id):
        return cls.db().fetch_all(_SELECT + ' WHERE r.user_id = ? ORDER BY r.created_at DESC, r.id DESC',
                                  (user_id,))

    @classmethod
    def list_filtered(cls, status_id=None, room_id=None, search=None, date_from=None, date_to=None):
        where, params = [], []
        if _to_int(status_id):
            where.append('r.status_id = ?'); params.append(_to_int(status_id))
        if _to_int(room_id):
            where.append('r.room_id = ?'); params.append(_to_int(room_id))
        if search:
            where.append('(u.login LIKE ? OR u.fio LIKE ?)')
            like = f'%{search.strip()[:50]}%'
            params += [like, like]
        if date_from:
            where.append('date(r.start_at) >= date(?)'); params.append(date_from)
        if date_to:
            where.append('date(r.start_at) <= date(?)'); params.append(date_to)
        sql = _SELECT + (' WHERE ' + ' AND '.join(where) if where else '') + ' ORDER BY r.created_at DESC, r.id DESC'
        return cls.db().fetch_all(sql, tuple(params))

    @classmethod
    def change_status(cls, request_id, new_status_id):
        req = cls.get_by_id(request_id)
        new_status_id = _to_int(new_status_id)
        if not req:
            return 'Заявка не найдена'
        if new_status_id not in (Status.ASSIGNED, Status.DONE):
            return 'Недопустимый статус'
        if new_status_id <= req.status_id:
            return 'Статус можно менять только вперёд'
        cls.db().execute('UPDATE request SET status_id = ? WHERE id = ?', (new_status_id, request_id))
        return ''

    @classmethod
    def summary_for_user(cls, user_id):
        row = cls.db().fetch_one(
            '''SELECT COUNT(*) AS total,
                      SUM(r.status_id = 1) AS new, SUM(r.status_id = 2) AS assigned, SUM(r.status_id = 3) AS done,
                      COUNT(rv.id) AS reviews,
                      MIN(CASE WHEN r.status_id = 2 THEN r.start_at END) AS next_event
               FROM request r LEFT JOIN review rv ON rv.request_id = r.id
               WHERE r.user_id = ?''', (user_id,))
        return {k: (v or 0) if k != 'next_event' else v for k, v in row.items()}

    @classmethod
    def stats(cls):
        rows = cls.db().fetch_all('SELECT status_id, COUNT(*) AS cnt FROM request GROUP BY status_id')
        result = {Status.NEW: 0, Status.ASSIGNED: 0, Status.DONE: 0}
        for r in rows:
            result[r['status_id']] = r['cnt']
        return result


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
