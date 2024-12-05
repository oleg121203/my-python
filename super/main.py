import eventlet
eventlet.monkey_patch()

import os
import discord
from discord.ext import commands
from spor import спор
from config import models, answers, questions, Config
from app import app, socketio
import asyncio

if __name__ == '__main__':
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    TOKEN_FILE = os.path.join(PROJECT_DIR, 'token.txt')

    # Создаем отдельную функцию для запуска бота
    async def start_discord_bot():
        try:
            with open(TOKEN_FILE, 'r') as f:
                token = f.read().strip()
            
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            intents.typing = True
            intents.presences = True
            intents.guilds = True
            intents.messages = True

            bot = commands.Bot(command_prefix='/', intents=intents)
            await bot.start(token)
        except Exception as e:
            print(f"Discord bot error: {e}")
            return None

    # Запускаем Flask и Socket.IO
    try:
        eventlet.spawn(start_discord_bot)
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=Config.DEBUG,
            use_reloader=False,
            allow_unsafe_werkzeug=True,
            cors_allowed_origins="*"
        )
    except Exception as e:
        print(f"Server error: {e}")

