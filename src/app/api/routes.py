from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from .. import socketio, debate_history
from . import bp
import uuid

@bp.route('/debates/active')
@login_required
def get_active_debates():
    active_debates = [
        {'id': k, **v}
        for k, v in debate_history.items()
        if v.get('status') == 'active'
    ]
    return jsonify(active_debates)

@socketio.on('start_debate')
def handle_debate_start(data):
    if not current_user.is_authenticated:
        return False
        
    debate_id = str(uuid.uuid4())
    debate_history[debate_id] = {
        'topic': data['topic'],
        'models': data['models'],
        'status': 'active',
        'messages': []
    }
    
    return {'success': True, 'debate_id': debate_id}