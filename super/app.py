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
        print(f"Бот запущено! Ім'я ��ористувача: {self.user.name}")


class Model1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def read_questions(self, file_name):
        try:
            with open(file_name, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []

    @commands.command(name='програма')
    async def програма(self, ctx, *, аргументи: str):
        try:
            if ':' not in аргументи:
                await ctx.send("Використання: /програма <тема>:<модель1>,<модель2>")
                return

            тема, моделі = аргументи.split(':', 1)
            questions_file = os.path.join(
                PROJECT_DIR, 'src', 'questions.txt')
            questions = self.read_questions(questions_file)

        except ValueError:
            await ctx.send("Використання: /програма <тема>:<модель1>,<модель2>")

    @commands.command(name='спор')
    async def спор_command(self, ctx, *, промт: str = None):
        try:
            if not промт:
                available_topics = ", ".join(answers.keys())
                await ctx.send(f"Укажите тему. Доступные темы: {available_topics}")
                return
            await спор(ctx, промт)
        except Exception as e:
            print(f"Error: {e}")

bot = Bot()

if __name__ == '__main__':
    from threading import Thread
    Thread(target=bot.run, args=(token,)).start()
    app.run(host='0.0.0.0', port=5000)
