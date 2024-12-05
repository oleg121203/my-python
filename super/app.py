from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField
import os
import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog, command
from spor import спор
from config import (
    models, 
    answers, 
    questions, 
    debate_settings, 
    debate_history, 
    default_settings
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

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
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/animate.css@4.1.1/animate.min.css" rel="stylesheet">
    <style>
        .debate-card {
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .debate-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .model-badge {
            background: linear-gradient(135deg, #7289da, #5b6eae);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">Discord Bot</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/debate">Новий спор</a>
                <a class="nav-link" href="/history">Історія</a>
                <a class="nav-link" href="/stats">Статистика</a>
            </div>
        </div>
    </nav>
    <div class="container py-4">
        {{ content | safe }}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script>
        const socket = io();
        
        socket.on('debate_update', function(data) {
            // Обновление UI при получении новых данных
            updateDebateUI(data);
        });
        
        function updateDebateUI(data) {
            // Добавление новых сообщений в чат
            const chatContainer = document.getElementById('debate-chat');
            if (chatContainer && data.message) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'alert alert-info animate__animated animate__fadeIn';
                messageDiv.textContent = data.message;
                chatContainer.appendChild(messageDiv);
                messageDiv.scrollIntoView({behavior: 'smooth'});
            }
        }
        
        function startDebate(settings) {
            socket.emit('start_debate', settings);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    content = """
    <h1>Discord Bot Dashboard</h1>
    <div class="command-block">
        <h2>О боте</h2>
        <p>Этот бот поддерживает следующие функции:</p>
        <div class="topic-list">
            <a href="/commands" class="button">Сравнение моделей</a>
            <a href="/commands" class="button">Работа с библиотеками</a>
        </div>
    </div>
    """
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/commands')
def commands():
    content = """
    <h1>Доступные команды</h1>
    <div class="command-block">
        <h3>Сравнение моделей</h3>
        <p>Сравнивает ответы разных моделей по заданной теме</p>
        <div class="topic-list">
            <strong>Доступные темы:</strong><br>
            """ + " ".join([f'<a href="#" class="button">{topic}</a>' for topic in answers.keys()]) + """
        </div>
        <p><strong>Использование:</strong> /спор &lt;тема&gt;:&lt;модель1&gt;,&lt;модель2&gt;</p>
    </div>
    
    <div class="command-block">
        <h3>Работа с библиотеками</h3>
        <p>Получает информацию о программных библиотеках</p>
        <div class="topic-list">
            <strong>Доступные м��дели:</strong><br>
            """ + " ".join([f'<a href="#" class="button">{model}</a>' for model in models]) + """
        </div>
        <p><strong>Использование:</strong> /програма &lt;тема&gt;:&lt;модель1&gt;,&lt;модель2&gt;</p>
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

@app.route('/debate')
def debate():
    content = """
    <div class="row">
        <div class="col-md-8">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h3 class="card-title">Налаштування спору</h3>
                    <form id="debate-form" class="needs-validation" novalidate>
                        <div class="mb-3">
                            <label class="form-label">Тема спору</label>
                            <select class="form-select" name="topic" required>
                                """ + "".join([
                                    f'<option value="{topic}">{topic}</option>' 
                                    for topic in answers.keys()
                                ]) + """
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Темп спору</label>
                            <div class="btn-group w-100" role="group">
                                """ + "".join([
                                    f'''
                                    <input type="radio" class="btn-check" name="speed" 
                                           id="speed_{speed}" value="{speed}" 
                                           {'checked' if speed == default_settings["speed"] else ''}>
                                    <label class="btn btn-outline-primary" for="speed_{speed}">
                                        {settings["name"]}<br>
                                        <small class="text-muted">{settings["description"]}</small>
                                    </label>
                                    ''' for speed, settings in debate_settings["speeds"].items()
                                ]) + """
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Тип відповідей</label>
                            <div class="btn-group w-100" role="group">
                                """ + "".join([
                                    f'''
                                    <input type="radio" class="btn-check" name="response_type" 
                                           id="response_{rtype}" value="{rtype}" 
                                           {'checked' if rtype == default_settings["response_type"] else ''}>
                                    <label class="btn btn-outline-primary" for="response_{rtype}">
                                        {settings["name"]}<br>
                                        <small class="text-muted">{settings["description"]}</small>
                                    </label>
                                    ''' for rtype, settings in debate_settings["response_types"].items()
                                ]) + """
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Дозволи</label>
                            <div class="d-flex flex-wrap gap-2">
                                """ + "".join([
                                    f'''
                                    <label class="tag">
                                        <input type="checkbox" name="permissions[]" 
                                               value="{perm}" 
                                               {'checked' if perm in default_settings["permissions"] else ''}>
                                        {desc}
                                    </label>
                                    ''' for perm, desc in debate_settings["permissions"].items()
                                ]) + """
                            </div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">Почати спор</button>
                    </form>
                </div>
            </div>
        </div>
        
        <div id="debate-chat" class="mt-4">
        </div>
    </div>
    """
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/start_debate', methods=['POST'])
def start_debate():
    topic = request.form.get('custom_topic')
    speed = request.form.get('speed')
    permissions = request.form.getlist('permissions[]')
    
    # Store debate settings
    debate_id = len(debate_history) + 1
    debate_history[debate_id] = {
        'topic': topic,
        'speed': speed,
        'permissions': permissions,
        'status': 'active'
    }
    
    return redirect(f'/debate/{debate_id}')

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
            await ctx.send("Використання: /програма <т��ма>:<модель1>,<модель2>")

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

@socketio.on('start_debate')
def handle_debate_start(settings):
    # Обработка начала спора через WebSocket
    debate_id = len(debate_history) + 1
    debate_history[debate_id] = {
        'settings': settings,
        'messages': [],
        'status': 'active'
    }
    emit('debate_update', {'debate_id': debate_id, 'status': 'started'})

if __name__ == '__main__':
    from threading import Thread
    Thread(target=bot.run, args=(token,)).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
