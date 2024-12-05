import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


models = ['Mixtral 8x7B', 'Qwen2.5', 'Coder 1.5B']

answers = {
    "AI Libraries": {
        "Mixtral 8x7B": {"answer": "Для створення програми слід використовувати бібліотеку «Mixtral», оскільки вона має дуже швидку роботу та ефективне використання ресурсів."},
        "Qwen2.5": {"answer": "Для створення програми слід використовувати бібліотеку «Qwen», оскільки вона має дуже добре спроєктовану архітектуру та високий рівень безпеки."},
        "Coder 1.5B": {"answer": "Для створення програми слід використовувати бібліотеку «Coder», оскільки вона має дуже добре підтримку багатьох мов програмування."}
    },
    "Telethon": {
        "Mixtral 8x7B": {"answer": "Telethon превосходит другие библиотеки благодаря асинхро��ности, полной поддержке MTProto и высокой производительности."},
        "Qwen2.5": {"answer": "Python-telegram-bot предпочтительнее Telethon из-за более простого API и лучшей документации."},
        "Coder 1.5B": {"answer": "Telethon - лучший выбор благодаря его гибкости и поддержке всех функций Telegram, включая пользовательские аккаунты."}
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
        "slow": {"name": "Повільний", "delay": 2.0, "description": "Детальне обговорення кожного аргументу"},
        "medium": {"name": "Середній", "delay": 1.0, "description": "Збалансований темп дискусії"},
        "fast": {"name": "Швидкий", "delay": 0.5, "description": "Швидкий о��мін аргументами"}
    },
    "response_types": {
        "short": {"name": "Короткі", "description": "Лаконічні відповіді по суті"},
        "detailed": {"name": "Детальні", "description": "Розгорнуті відповіді з аргументацією"},
        "mixed": {"name": "Змішані", "description": "Комбінація коротких та детальних відповідей"}
    },
    "interaction_modes": {
        "sequential": {"name": "Послідовний", "description": "Моделі відповідають по черзі"},
        "interactive": {"name": "Інтерактивний", "description": "Моделі можуть взаємодіяти між собою"}
    },
    "permissions": {
        "model_discussion": "Дозвіл моделям обговорювати між собою",
        "question_clarification": "Дозвіл уточнювати питання",
        "user_clarification": "Дозвіл запитувати уточнення у користувача"
    }
}

# Добавляем настройки по умолчанию
default_settings = {
    "speed": "medium",
    "response_type": "detailed",
    "interaction_mode": "interactive",
    "permissions": ["model_discussion", "question_clarification"]
}

# История дебатов с расширенной структурой
debate_history = {}

# Добавляем обработку ошибок при инициализации
try:
    debate_settings = debate_settings
except NameError:
    debate_settings = {
        "speeds": {
            "medium": {"name": "Середній", "delay": 1.0, "description": "Збалансований темп дискусії"}
        },
        "permissions": {}
    }

try:
    default_settings
except NameError:
    default_settings = {
        "speed": "medium",
        "response_type": "detailed",
        "interaction_mode": "interactive",
        "permissions": []
    }
