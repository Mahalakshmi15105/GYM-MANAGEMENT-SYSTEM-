from flask import Blueprint

members_bp = Blueprint('members', __name__)

@members_bp.route('')
def test():
    return {'status': 'working'}
