from flask import Blueprint, jsonify, render_template, request

from backend.models.reference import Room, Status
from backend.models.request import Request
from backend.security.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.get('/admin')
@admin_required
def admin_page():
    return render_template('admin.html', statuses=Status.get_all(), rooms=Room.get_all(),
                           stats=Request.stats())


@admin_bp.get('/api/admin/requests')
@admin_required
def api_requests():
    args = request.args
    items = Request.list_filtered(
        status_id=args.get('status'), room_id=args.get('room'),
        search=args.get('q'), date_from=args.get('from'), date_to=args.get('to'),
    )
    return jsonify(requests=items, stats=Request.stats())


@admin_bp.patch('/api/admin/requests/<int:request_id>/status')
@admin_required
def api_change_status(request_id):
    data = request.get_json(silent=True) or {}
    error = Request.change_status(request_id, data.get('status_id'))
    if error:
        return jsonify(error=error), 400
    return jsonify(message='Статус обновлён', stats=Request.stats())
