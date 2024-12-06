
from flask import Blueprint, render_template, redirect, url_for, flash
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth_bp', __name__)

# ...existing routes and logic...