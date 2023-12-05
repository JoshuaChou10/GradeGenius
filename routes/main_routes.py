from flask import session, render_template,Blueprint
from flask_bcrypt import Bcrypt
from models import User,Course
from app import app
from flask import session
from app import db
from helpers import get_guest_GPA,get_guest_total_study




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    GPA=0.0
    timeStudied,timeLeft=0.0,0.0
    if 'user_id' in session:
        user=User.query.get(session['user_id'])
        if user:
            GPA=user.get_GPA()
            timeStudied,timeLeft=user.get_study_goals()
    else:
        GPA=get_guest_GPA()
        timeLeft=get_guest_total_study()

    return render_template('dashboard.html',GPA=GPA,timeStudied=timeStudied,timeLeft=timeLeft)
