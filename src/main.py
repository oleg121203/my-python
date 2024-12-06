from app import create_app, socketio, bot
from config import Config
import eventlet
import os

app = create_app(Config)

def run_discord_bot(token):
    try:
        bot.run(token)
    except Exception as e:
        print(f"Discord bot error: {e}")

if __name__ == '__main__':
    # Read token
    token_path = os.path.join(os.path.dirname(__file__), 'token.txt')
    with open(token_path) as f:
        token = f.read().strip()

    # Start bot in background
    eventlet.spawn(run_discord_bot, token)
    
    # Run Flask app
    socketio.run(
        app,
        host='0.0.0.0', 
        port=5000,
        debug=Config.DEBUG,
        use_reloader=False
    )
