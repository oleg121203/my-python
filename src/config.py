import os

class Config:
    # Базовые настройки
    INSTANCE_PATH = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    DEBUG = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(INSTANCE_PATH, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Socket.IO
    SOCKETIO_ASYNC_MODE = 'eventlet'
    CORS_ALLOWED_ORIGINS = ['http://localhost:5000']

# AI Models configuration
models = ['Mixtral 8x7B', 'Qwen2.5', 'Coder 1.5B']

answers = {
    "AI Libraries": {
        "Mixtral 8x7B": {"answer": "Для створення програми слід використовувати бібліотеку «Mixtral��..."},
        "Qwen2.5": {"answer": "Для створення програми слід використовувати бібліотеку «Qwen»..."},
        "Coder 1.5B": {"answer": "Для створення програми слід використовувати бібліотеку «Coder»..."}
    }
}

questions = {
    "AI Libraries": {
        "Mixtral 8x7B": ["Що таке Mixtral?", "Які переваги має Mixtral?"],
        "Qwen2.5": ["Що таке Qwen?", "Які особливості має Qwen?"],
        "Coder 1.5B": ["Що таке Coder?", "Які можливості має Coder?"]
    }
}

debate_settings = {
    "speeds": {
        "slow": {"name": "Повільний", "delay": 2.0, "description": "Детальне обговорення"},
        "medium": {"name": "Середній", "delay": 1.0, "description": "Збалансований темп"},
        "fast": {"name": "Швидкий", "delay": 0.5, "description": "Швидкий обмін"}
    },
    "response_types": {
        "short": {"name": "Короткі", "description": "Лаконічні відповіді"},
        "detailed": {"name": "Детальні", "description": "Розгорнуті відповіді"}
    }
}

default_settings = {
    "speed": "medium",
    "response_type": "detailed",
    "interaction_mode": "interactive",
    "permissions": ["model_discussion", "question_clarification"]
}

# Initialize empty debate history
debate_history = {}