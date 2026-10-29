from backend.models.base_model import BaseModel
from backend.models.reference import Status
from backend.validators.validators import Validator


class Review(BaseModel):
    table = 'review'

    @classmethod
    def create(cls, user_id, request_id, text, rating):
        req = cls.db().fetch_one('SELECT * FROM request WHERE id = ? AND user_id = ?',
                                 (request_id, user_id))
        if not req:
            return None, {'form': 'Заявка не найдена'}
        if req['status_id'] != Status.DONE:
            return None, {'form': 'Отзыв можно оставить только после завершения мероприятия'}
        if cls.db().fetch_one('SELECT id FROM review WHERE request_id = ?', (request_id,)):
            return None, {'form': 'Отзыв по этой заявке уже оставлен'}

        errors = {'text': Validator.review_text(text), 'rating': Validator.rating(rating)}
        errors = {k: v for k, v in errors.items() if v}
        if errors:
            return None, errors
        review_id = cls.db().execute(
            'INSERT INTO review (request_id, text, rating) VALUES (?, ?, ?)',
            (request_id, text.strip(), int(rating)),
        )
        return cls(id=review_id, request_id=request_id, text=text.strip(), rating=int(rating)), {}
