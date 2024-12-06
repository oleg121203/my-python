#-----------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
#-----------------------------------------------------------------------------------------

from flask import Flask
from auth_bp import auth_bp
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route("/")
def hello():
    return app.send_static_file("index.html")
