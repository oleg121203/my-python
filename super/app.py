from flask import Flask, request, jsonify
import os
import discord
from discord.ext import commands
from spor import спор
from config import models, answers, questions

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(PROJECT_DIR, 'token.txt')

try:
    with open(TOKEN_FILE, 'r') as f:
        token = f.read().strip()
except FileNotFoundError:
    print(f"Помилка: Файл {TOKEN_FILE} не знайдено")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.typing = True
intents.presences = True
intents.guilds = True
intents.messages = True


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)

    async def setup_hook(self):
        await self.add_cog(Model1(self))

    async def on_ready(self):
        print(f"Бот запущено! Ім'я користувача: {self.user.name}")


class Model1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def read_questions(self,

    app.run(host='0.0.0.0', port=5000)
    app.run(host='0.0.0.0', port=5000)