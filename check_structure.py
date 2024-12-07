import os


def check_structure():
    required_dirs = [
        'app',
        'app/api',
        'app/auth',
        'app/discord',
        'app/models',
        'instance',
        'static/css',
        'templates'
    ]

    required_files = [
        'app/__init__.py',
        'app/api/__init__.py',
        'app/api/routes.py',
        'app/auth/__init__.py',
        'app/auth/routes.py',
        'app/discord/__init__.py',
        'app/discord/bot.py',
        'app/models/__init__.py',
        'app/models/user.py',
        'config.py',
        'main.py',
        'requirements.txt'
    ]

    missing = []

    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing.append(f"Directory missing: {dir_path}")

    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(f"File missing: {file_path}")

    if missing:
        print("Missing items:")
        for item in missing:
            print(f"- {item}")
    else:
        print("All required files and directories are present!")


if __name__ == '__main__':
    check_structure()
