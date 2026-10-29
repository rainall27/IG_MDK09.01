from backend.database import Database


class BaseModel:
    table = None

    def __init__(self, **fields):
        for key, value in fields.items():
            setattr(self, key, value)

    @classmethod
    def db(cls):
        return Database()

    @classmethod
    def get_by_id(cls, obj_id):
        row = cls.db().fetch_one(f'SELECT * FROM {cls.table} WHERE id = ?', (obj_id,))
        return cls(**row) if row else None

    @classmethod
    def get_all(cls, order_by='id'):
        rows = cls.db().fetch_all(f'SELECT * FROM {cls.table} ORDER BY {order_by}')
        return [cls(**r) for r in rows]

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def validate(self):
        return {}
