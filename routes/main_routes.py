from flask import session, render_template
from models import User
from app import app
from flask import session
from app import db
from helpers import get_guest_GPA,get_guest_total_study
from datetime import datetime
import uuid

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
        if 'temporary_courses' not in session:
            session['temporary_courses']= [{
                    'id': int(uuid.uuid4()),
                    'code': 'MHF4UO',
                    'description':'This is a preview course for guest users. Try adding an assessment below!',
                    'name': 'Advanced Functions',
                    "creation_date": datetime.today(),
                    'end_date':datetime.today() ,
                    'assessments': [],
                    'starting_grade':94,
                    'starting_marks':200,
                    'grade':94,
                    'total_marks':200,
                    'goal': 98,
                    'total_study':1200,
                    'time_studied':0
            }]
        GPA=get_guest_GPA(session.get('temporary_courses',[])) 
        timeLeft=get_guest_total_study(session.get('temporary_courses',[]))
    return render_template('dashboard.html',GPA=GPA,timeStudied=timeStudied,timeLeft=timeLeft)
