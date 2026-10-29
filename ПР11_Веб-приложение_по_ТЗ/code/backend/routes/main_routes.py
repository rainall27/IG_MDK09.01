from flask import Blueprint, render_template

from backend.models.reference import Room

main_bp = Blueprint('main', __name__)


@main_bp.get('/')
def index():
    return render_template('index.html', rooms=Room.get_all())
