from flask import session, render_template,Blueprint
from flask_bcrypt import Bcrypt
from models import User,Course
from app import app
from flask import session
from app import db
from helpers import get_guest_GPA




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    GPA=0.0
    if 'user_id' in session:
        user=User.query.get(session['user_id'])
        if user:
            GPA=user.get_GPA()
    else:
        GPA=get_guest_GPA()

    return render_template('dashboard.html',GPA=GPA)
