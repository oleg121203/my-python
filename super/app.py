from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # Добавляем CORS
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField
import os
import json
from datetime import datetime
import discord
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
CORS(app, resources={r"/*": {"origins": "*"}})  # Разрешаем все источники
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")  # Разрешаем CORS для socketio

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
                <a class="nav-link" href="/debate">Новий сп��р</a>
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
            <strong>Доступные модели:</strong><br>
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
        
        <div class="col-md-4">
            <div class="card shadow-sm mb-4">
                <div class="card-body">
                    <h4>Створення нової теми</h4>
                    <form id="custom-topic-form">
                        <div class="mb-3">
                            <label class="form-label">Назва теми</label>
                            <input type="text" class="form-control" name="topic_name" placeholder="Введіть назву теми">
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Промпт для моделей</label>
                            <textarea class="form-control" name="prompt" rows="4" 
                                    placeholder="Опишіть контекст та деталі спору..."></textarea>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Ключові аспекти</label>
                            <div class="input-group mb-2">
                                <input type="text" class="form-control" placeholder="Додайте ключовий аспект">
                                <button class="btn btn-outline-secondary" type="button" onclick="addAspect()">+</button>
                            </div>
                            <div id="aspects-list" class="d-flex flex-wrap gap-2">
                                <!-- Аспекты будут добавляться сюда -->
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Обмеження спору</label>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="constraints[]" value="fact_based">
                                <label class="form-check-label">Тільки факти</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="constraints[]" value="time_limit">
                                <label class="form-check-label">Обмеження часу</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="constraints[]" value="sources_required">
                                <label class="form-check-label">Потрібні джерела</label>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100">Створити тему</button>
                    </form>
                </div>
            </div>
            
            <div class="card shadow-sm">
                <div class="card-body">
                    <h4>Поточні спори</h4>
                    <div id="active-debates" class="list-group">
                        <!-- Активные споры будут добавляться сюда -->
                    </div>
                </div>
            </div>
        </div>
        
        <div id="debate-chat" class="mt-4">
        </div>
    </div>

    <script>
        let aspects = [];
        
        function addAspect() {
            const input = document.querySelector('.input-group input');
            const aspect = input.value.trim();
            if (aspect) {
                aspects.push(aspect);
                updateAspectsList();
                input.value = '';
            }
        }
        
        function removeAspect(index) {
            aspects.splice(index, 1);
            updateAspectsList();
        }
        
        function updateAspectsList() {
            const list = document.getElementById('aspects-list');
            list.innerHTML = aspects.map((aspect, index) => `
                <span class="badge bg-secondary">
                    ${aspect}
                    <button type="button" class="btn-close btn-close-white" 
                            onclick="removeAspect(${index})"></button>
                </span>
            `).join('');
        }
        
        document.getElementById('custom-topic-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            formData.append('aspects', JSON.stringify(aspects));
            
            fetch('/create_topic', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновляем список тем
                    socket.emit('update_topics');
                }
            });
        });
    </script>
    """
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/create_topic', methods=['POST'])
def create_topic():
    topic_name = request.form.get('topic_name')
    prompt = request.form.get('prompt')
    aspects = json.loads(request.form.get('aspects', '[]'))
    constraints = request.form.getlist('constraints[]')
    
    # Добавляем новую тему в конфиг
    new_topic = {
        'prompt': prompt,
        'aspects': aspects,
        'constraints': constraints,
        'created_at': datetime.now().isoformat()
    }
    
    debate_settings['custom_topics'] = debate_settings.get('custom_topics', {})
    debate_settings['custom_topics'][topic_name] = new_topic
    
    return jsonify({'success': True, 'topic': topic_name})

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
    async def programa(self, ctx, *, arguments: str):
        try:
            if ':' not in arguments:
                await ctx.send("Використання: /програма <тема>:<модель1>,<модель2>")
                return

            topic, models_list = arguments.split(':', 1)
            questions_file = os.path.join(
                PROJECT_DIR, 'src', 'questions.txt')
            questions = self.read_questions(questions_file)

        except ValueError:
            await ctx.send("Використання: /програма <тема>:<модель1>,<модель2>")

    @command(name='спор')
    async def spor_command(self, ctx, *, promt: str = None):
        try:
            if not promt:
                available_topics = ", ".join(answers.keys())
                await ctx.send(f"Укажите тему. Доступные темы: {available_topics}")
                return
            await спор(ctx, promt)
        except Exception as e:
            print(f"Error: {e}")

bot = DiscordBot()

def run_bot():
    bot.run(token)

if __name__ == '__main__':
    from threading import Thread
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True  # Делаем поток демоном
    bot_thread.start()
    
    # Run Flask app with updated settings
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False,
        allow_unsafe_werkzeug=True  # Разрешаем небезопасный доступ для разработки
    )

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
