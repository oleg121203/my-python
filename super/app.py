from flask import Flask, request, jsonify, render_template_string
import os
import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog, command
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

# Базовый HTML шаблон
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Discord Bot Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .nav {
            background-color: #7289DA;
            padding: 10px;
            margin-bottom: 20px;
        }
        .nav a {
            color: white;
            text-decoration: none;
            margin-right: 15px;
        }
        .content {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
        }
        .command {
            background-color: white;
            padding: 10px;
            margin: 10px 0;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Главная</a>
        <a href="/commands">Команды</a>
        <a href="/status">Статус</a>
    </div>
    <div class="content">
        {{ content | safe }}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    content = """
    <h1>Discord Bot Dashboard</h1>
    <div class="command">
        <h2>О боте</h2>
        <p>Этот бот поддерживает следующие функции:</p>
        <ul>
            <li>Команда /спор - сравнение ответов разных моделей</li>
            <li>Команда /програма - работа с программными библиотеками</li>
        </ul>
    </div>
    """
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/commands')
def commands():
    content = """
    <h1>Доступные команды</h1>
    <div class="command">
        <h3>/спор &lt;тема&gt;:&lt;модель1&gt;,&lt;модель2&gt;</h3>
        <p>Сравнивает ответы разных моделей по заданной теме</p>
        <p>Доступные темы: """ + ", ".join(answers.keys()) + """</p>
    </div>
    <div class="command">
        <h3>/програма &lt;тема&gt;:&lt;модель1&gt;,&lt;модель2&gt;</h3>
        <p>Получает информацию о программных библиотеках</p>
    </div>
    """
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/status')
def status():
    content = """
    <h1>Статус бота</h1>
    <div class="command">
        <p>Статус: Активен</p>
        <p>Доступные модели: """ + ", ".join(models) + """</p>
    </div>
    """
    return render_template_string(BASE_TEMPLATE, content=content)

@app.errorhandler(404)
def not_found(error):
    content = "<p>Страница не найдена!</p>"
    return render_template_string(BASE_TEMPLATE, content=content), 404


class DiscordBot(Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)

    async def setup_hook(self):
        await self.add_cog(Model1(self))

    async def on_ready(self):
        print(f"Бот запущено! Ім'я користувача: {self.user.name}")


class Model1(Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    def read_questions(self, file_name):
        try:
            with open(file_name, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []

    @command(name='програма')
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

    @command(name='спор')
    async def спор_command(self, ctx, *, промт: str = None):
        try:
            if not промт:
                available_topics = ", ".join(answers.keys())
                await ctx.send(f"Укажите тему. Доступные темы: {available_topics}")
                return
            await спор(ctx, промт)
        except Exception as e:
            print(f"Error: {e}")

bot = DiscordBot()

if __name__ == '__main__':
    from threading import Thread
    Thread(target=bot.run, args=(token,)).start()
    app.run(host='0.0.0.0', port=5000)
