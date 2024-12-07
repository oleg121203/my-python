from app import create_app, socketio
from config import Config
import eventlet
import os

eventlet.monkey_patch()

def run_discord_bot(token):
    try:
        from app.discord import init_bot
        bot = init_bot(app)
        if bot:
            bot.run(token)
    except Exception as e:
        app.logger.error(f"Discord bot error: {e}")

app = create_app(Config)

if __name__ == '__main__':
    # Read token
    token_path = os.path.join(os.path.dirname(__file__), 'token.txt')
    try:
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
    except Exception as e:
        print(f"Error starting application: {e}")
