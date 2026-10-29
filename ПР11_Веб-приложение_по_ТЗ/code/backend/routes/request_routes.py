from flask import Blueprint, jsonify, render_template, request, session, url_for

from backend.models.reference import PaymentMethod, Room
from backend.models.request import Request
from backend.models.review import Review
from backend.models.user import User
from backend.security.decorators import participant_required

request_bp = Blueprint('requests', __name__)


@request_bp.get('/dashboard')
@participant_required
def dashboard():
    return render_template('dashboard.html', requests=Request.list_for_user(session['user_id']))


@request_bp.get('/profile')
@participant_required
def profile():
    user = User.get_by_id(session['user_id'])
    return render_template('profile.html', user=user, summary=Request.summary_for_user(user.id))


@request_bp.get('/requests/new')
@participant_required
def create_page():
    return render_template('create_request.html',
                           rooms=Room.get_all(), payments=PaymentMethod.get_all())


@request_bp.get('/api/requests')
@participant_required
def api_my_requests():
    return jsonify(requests=Request.list_for_user(session['user_id']))


@request_bp.post('/api/requests')
@participant_required
def api_create_request():
    data = request.get_json(silent=True) or {}
    req, errors = Request.create(
        user_id=session['user_id'],
        room_id=data.get('room_id'),
        payment_method_id=data.get('payment_method_id'),
        start_at=str(data.get('start_at', '')),
    )
    if errors:
        return jsonify(errors=errors), 422
    return jsonify(message='Заявка отправлена администратору', id=req.id,
                   redirect=url_for('requests.dashboard')), 201


@request_bp.post('/api/requests/<int:request_id>/review')
@participant_required
def api_create_review(request_id):
    data = request.get_json(silent=True) or {}
    review, errors = Review.create(session['user_id'], request_id,
                                   str(data.get('text', '')), data.get('rating'))
    if errors:
        code = 422 if 'form' not in errors else 409
        return jsonify(errors=errors), code
    return jsonify(message='Спасибо за отзыв!', review=review.to_dict()), 201
