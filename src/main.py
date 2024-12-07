import eventlet
eventlet.monkey_patch()

from app import create_app, socketio
from config import Config
import os

app = create_app(Config)

if __name__ == '__main__':
    # Run Flask app
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG,
        use_reloader=False
    )
