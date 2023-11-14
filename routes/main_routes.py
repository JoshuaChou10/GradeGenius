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
    user = None  
    if 'user_id' in session:
        courses = Course.query.filter_by(user_id=session['user_id']).all()
        user = User.query.filter_by(id=session['user_id']).first()
    else:
        courses = session.get('temporary_courses', [])
    return render_template('dashboard.html')
