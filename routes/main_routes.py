from flask import session, render_template,Blueprint
from flask_bcrypt import Bcrypt
from models import User,Course
from app import app
from flask import session
from app import db





@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
