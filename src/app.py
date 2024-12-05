from flask import Flask, request, jsonify, render_template, redirect, url_for, render_template_string, flash
from flask_socketio import SocketIO, emit
from flask_cors import CORS
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
    default_settings,
    Config
)
import asyncio
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Initialize admin
    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
    admin.add_view(SecureModelView(User, db.session))

    # Initialize SocketIO
    socketio = SocketIO(
        app,
        async_mode='eventlet',
        logger=True,
        engineio_logger=True,
        ping_timeout=60
    )

    # Register routes here
    # ...existing code...

    return app, socketio


from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

# ...existing code...

app, socketio = create_app(Config)

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
                <a class="nav-link" href="/debate">Новий спір</a>
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

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))

        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Update existing route decorators to require login


@app.route('/')
@login_required
def home():
    return render_template('home.html',
                           title='Головна',
                           bot_status='Активний',
                           active_debates=len(debate_history))


@app.route('/models')
@login_required
def models_page():
    # Загружаем конфигурацию моделей из файла Continue
    continue_config_path = os.path.expanduser('~/.continue/config.json')
    try:
        with open(continue_config_path, 'r') as f:
            continue_config = json.load(f)
            model_info = continue_config.get('models', [])
    except FileNotFoundError:
        model_info = []

    return render_template('models.html',
                           title='Моделі',
                           model_info=model_info,
                           model_capabilities=answers)


@app.route('/stats')
@login_required
def stats():
    stats_data = {
        'total_debates': len(debate_history),
        'active_debates': len([d for d in debate_history.values() if d['status'] == 'active']),
        'model_usage': {model: 0 for model in models}
    }
    return render_template('stats.html', title='Статистика', stats=stats_data)


@app.route('/commands')
@login_required
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
@login_required
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


@app.route('/debate/start', methods=['POST'])
def start_new_debate():
    try:
        data = request.get_json()
        selected_models = data.get('models', [])

        if len(selected_models) < 2:
            return jsonify({
                'success': False,
                'error': 'Потрібно вибрати мінімум 2 моделі'
            })

        debate_id = len(debate_history) + 1
        debate_history[debate_id] = {
            'models': selected_models,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'messages': []
        }

        socketio.emit('debate_started', {
            'debate_id': debate_id,
            'models': selected_models
        })

        return jsonify({
            'success': True,
            'debate_id': debate_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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

    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
        log_output=True
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


@socketio.on('select_model')
def handle_model_selection(data):
    model = data.get('model')
    debate_id = data.get('debate_id', 'current')

    if 'current_debate' not in debate_history:
        debate_history['current_debate'] = {
            'models': [],
            'status': 'preparing',
            'settings': {},
            'created_at': datetime.now().isoformat()
        }

    current_debate = debate_history['current_debate']

    if model not in current_debate['models']:
        current_debate['models'].append(model)
        emit('model_selected', {
            'success': True,
            'model': model,
            'models': current_debate['models']
        }, broadcast=True)


@app.route('/history')
@login_required
def debate_history_page():
    # Сортируем дебаты по дате создания
    sorted_debates = sorted(
        [{'id': k, **v}
            for k, v in debate_history.items() if k != 'current_debate'],
        key=lambda x: x.get('created_at', ''),
        reverse=True
    )

    return render_template('history.html',
                           title='Історія спорів',
                           debates=sorted_debates)


@app.route('/api/debates/active')
@login_required
def get_active_debates():
    active_debates = [
        {'id': k, **v}
        for k, v in debate_history.items()
        if isinstance(k, int) and v.get('status') == 'active'
    ]
    return jsonify(active_debates)


@app.route('/api/debates/<int:debate_id>/stop', methods=['POST'])
@login_required
def stop_debate(debate_id):
    if debate_id in debate_history:
        debate_history[debate_id]['status'] = 'completed'
        socketio.emit('debate_update', {
            'type': 'stop',
            'debate_id': debate_id
        })
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Debate not found'}), 404

# ...rest of existing code...


@socketio.on('start_debate')
def handle_debate_start(data):
    topic = data.get('topic')
    if topic:
        debate_id = len(debate_history) + 1
        debate_history[debate_id] = {
            'id': debate_id,
            'topic': topic,
            'status': 'active',
            'messages': []
        }
        emit('debate_message', {
             'message': f'Спор розпочато: {topic}'}, broadcast=True)
        asyncio.create_task(run_debate(debate_id))


async def run_debate(debate_id):
    debate = debate_history[debate_id]
    try:
        while debate['status'] == 'active':
            # Simulate debate progress
            await asyncio.sleep(5)
            message = f"Оновлення спору {debate_id}: {debate['topic']}"
            socketio.emit('debate_message', {'message': message})
    except Exception as e:
        socketio.emit('debate_message', {'message': f'Помилка: {str(e)}'})


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('status', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, debug=True)

# Расширяем конфигурацию
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Настраиваем Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Настраиваем админ-панель


class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(SecureModelView(User, db.session))

# Добавляем новые маршруты


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Создаем базу данных и админа при первом запуске


@app.before_first_request
def create_admin():
    db.create_all()
    if not User.query.filter_by(username='oleg').first():
        admin = User(username='oleg', is_admin=True)
        admin.set_password('oleg')
        db.session.add(admin)
        db.session.commit()


from app import create_app
from app.models import db, User

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Проверяем подключение к БД и наличие таблиц
        try:
            db.create_all()
            print("Database tables created successfully")
            
            # Создаем тестового пользователя если его нет
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', is_admin=True)
                admin.set_password('admin')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    app.run(debug=True)
