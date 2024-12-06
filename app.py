#-----------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
#-----------------------------------------------------------------------------------------

from flask import Flask
from auth_bp import auth_bp
from config import Config
from models import db, User
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_bp.login'  # Обновлено на 'auth_bp.login'

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def hello():
    return app.send_static_file("index.html")
