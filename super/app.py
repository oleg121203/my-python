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
        /* Modern CSS Reset */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            line-height: 1.6;
            background: #f0f2f5;
            color: #1a1a1a;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .nav {
            background: linear-gradient(135deg, #7289da, #5b6eae);
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .button {
            background: #7289da;
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            text-decoration: none;
            display: inline-block;
        }
        
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(114,137,218,0.3);
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .topic-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .settings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .tag {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            background: #e9ecef;
            margin: 4px;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="nav">
        <div class="container">
            <a href="/" class="button">Головна</a>
            <a href="/commands" class="button">Команди</a>
            <a href="/debate" class="button">Новий спор</a>
            <a href="/history" class="button">Історія</a>
            <a href="/status" class="button">Статус</a>
        </div>
    </div>
    <div class="container">
        {{ content | safe }}
    </div>
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
    <div class="card">
        <h2>Налаштування нового спору</h2>
        <form action="/start_debate" method="post">
            <div class="settings-grid">
                <div class="card">
                    <h3>Тема спору</h3>
                    <div class="topic-grid">
                        """ + "".join([f'''
                        <button type="button" class="button" onclick="setTopic('{topic}')">{topic}</button>
                        ''' for topic in answers.keys()]) + """
                    </div>
                    <input type="text" name="custom_topic" placeholder="Або введіть свою тему" class="input">
                </div>
                
                <div class="card">
                    <h3>Темп спору</h3>
                    """ + "".join([f'''
                    <label class="tag">
                        <input type="radio" name="speed" value="{speed}"> {desc}
                    </label>
                    ''' for speed, desc in debate_settings['speeds'].items()]) + """
                </div>
                
                <div class="card">
                    <h3>Налаштування відповідей</h3>
                    """ + "".join([f'''
                    <label class="tag">
                        <input type="checkbox" name="permissions[]" value="{perm}"> {desc}
                    </label>
                    ''' for perm, desc in debate_settings['permissions'].items()]) + """
                </div>
            </div>
            
            <div class="card">
                <button type="submit" class="button">Почати спор</button>
            </div>
        </form>
    </div>
    <script>
        function setTopic(topic) {
            document.querySelector('input[name="custom_topic"]').value = topic;
        }
    </script>
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
