from app import create_app
from config import Config
import eventlet
eventlet.monkey_patch()

app = create_app(Config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)