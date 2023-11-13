from functools import wraps
from flask import session, request, redirect, url_for, render_template,flash
from flask_bcrypt import Bcrypt
from models import User,Course, Assessment
from app import app
from flask import session
from app import db
 
bcrypt = Bcrypt(app)
@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
    return dict(user=user)

def check_course_ownership(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "user_id" in session:
            course_id = kwargs.get('course_id')
            #will overflow if signed in user tries to access guest user id
            try:
                course = Course.query.filter_by(id=course_id, user_id=session['user_id']).first()
            except OverflowError:
                 return render_template("not_found.html") 
            if not course:
                return render_template("not_found.html") 

        return func(*args, **kwargs)
    return decorated_function


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if a user with this username already exists
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flash('This username is already taken. Please choose another one.', 'danger')
            return redirect(url_for('signup'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password,GPA=0,goal=0)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = str(new_user.id)
        
        # Handling temporary courses for the newly registered user
        if 'temporary_courses' in session:
            temp_courses_data = session['temporary_courses']
            for course_data in temp_courses_data:
                temp_course=Course(user_id=session['user_id'],
                                code=course_data["code"],
                                name=course_data["name"],
                                end_date=course_data["end_date"], 
                                starting_grade=course_data["starting_grade"],
                                starting_marks=course_data["starting_marks"],
                                grade=course_data["grade"],
                                total_marks=course_data["total_marks"],
                                goal=course_data["goal"])
         
                db.session.add(temp_course)
                db.session.flush()  # to get an ID for the new course before committing
                for assessment_data in course_data['assessments']:
                    new_assessment = Assessment(name=assessment_data['name'], date=assessment_data['date'], earned=assessment_data['earned'], total=assessment_data['total'], course_id=temp_course.id)
                    db.session.add(new_assessment)
                db.session.commit()
            session.pop('temporary_courses', None)
        
        return redirect(url_for('dashboard'))
    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate the user using the provided credentials
        user = User.query.filter_by(username=username).first()
        

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash(f'Logged in as {user.username}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))
