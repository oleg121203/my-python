
from discord.ext import commands
import discord
from config import Config
import os

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='/', intents=intents)
    
    # ...existing code...

def init_bot(app):
    token_path = os.path.join(app.root_path, '..', 'token.txt')
    try:
        with open(token_path) as f:
            token = f.read().strip()
        bot = DiscordBot()
        return bot
    except Exception as e:
        app.logger.error(f"Failed to initialize Discord bot: {e}")
        return None