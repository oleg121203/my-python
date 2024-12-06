from app import create_app, socketio, bot
from config import Config
from discord.ext import commands
import discord
import os
import eventlet
eventlet.monkey_patch()


def run_discord_bot(token):
    try:
        bot.run(token)
    except Exception as e:
        print(f"Discord bot error: {e}")


app = create_app()

if __name__ == '__main__':
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    TOKEN_FILE = os.path.join(PROJECT_DIR, 'token.txt')

    try:
        with open(TOKEN_FILE, 'r') as f:
            token = f.read().strip()

        # Запускаем бота в отдельном потоке
        eventlet.spawn(run_discord_bot, token)

        # Запускаем Flask приложение
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=Config.DEBUG,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
    except Exception as e:
        print(f"Server error: {e}")
