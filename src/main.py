# Важно: eventlet.monkey_patch() должен быть первым импортом
import eventlet
eventlet.monkey_patch()

from app import create_app, socketio, db
from config import Config

def create_tables():
    with app.app_context():
        db.create_all()

app = create_app(Config)

if __name__ == '__main__':
    create_tables()
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG,
        use_reloader=False
    )
