from flask import session, request, redirect, url_for, render_template,Flask,flash,jsonify

from flask_bcrypt import Bcrypt
from sqlalchemy import asc
import math
import uuid
from datetime import datetime
from models import User,Course, Assessment
from app import app
from flask import session
from app import db

 # Method to calculate days remaining for the course to end
bcrypt = Bcrypt(app)

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
    return dict(user=user)




# def course_existing(course_name):
#     if 'user_id' in session:
#         course = Course.query.filter_by(name=course_name, user_id=session['user_id']).first()
#         return course is not None
#     else:
#         courses = session.get('temporary_courses', [])
#         for course in courses:
#             if course["name"]==course_name:
#                 return True
#         return False

   

    

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
    return render_template('dashboard.html', courses=courses, user=user)



#TODO, add error handling, if id does not exist
@app.route('/course/<int:course_id>')
def course_details(course_id):
    course=None
    time_left = 0
    if 'user_id' in session:
       
        course = Course.query.filter_by(id=course_id,user_id=session["user_id"]).first()
     
    
        if not course:
             return render_template("not_found.html")
        days_left=course.days_remaining()
        time_left = days_left

    else:
        temporary_courses = session.get('temporary_courses', [])  # Use .get() to avoid KeyError
        for c in temporary_courses:
            if c['id'] == course_id:
                course=c
                time_left=(c['end_date'].replace(tzinfo=None)-datetime.utcnow()).days
        if not course:
            return render_template("not_found.html")
        
    return render_template('course_details.html', course=course,time_left=time_left if time_left>0 else 0)



@app.route('/course/create', methods=['POST', 'GET'])
def create_course():
   
    if request.method == 'POST':
        # Extract the course data from the form
        course_name = request.form.get('course_name')
     
        
        course_code = request.form.get('course_code')
        end_date_str= request.form.get('end_date')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # Assuming end_date is in 'YYYY-MM-DD' format
        grade= request.form.get('grade')
        if not grade:
            grade=0.0
        else:
            grade = float(grade)
        total_marks=request.form.get('total_marks')
        if not total_marks:
            total_marks=0.0
        else:
            total_marks = float(total_marks)
        goal = float(request.form.get('goal'))

        # If the user is logged in, store the course in the database
        if 'user_id' in session:
            user_id = session['user_id']
            new_course = Course(user_id=user_id,
                                code=course_code,
                                name=course_name,
                                end_date=end_date, 
                                starting_grade=grade,
                                starting_marks=total_marks,
                                grade=grade,
                                total_marks=total_marks,
                                goal=goal)
            db.session.add(new_course)
            db.session.commit()
            return redirect(url_for('course_details', course_id=new_course.id))
        # If the user is not logged in, store the course data temporarily in the session
        else:
       
            
            if 'temporary_courses' not in session:
                session['temporary_courses'] = []

          
            temp_id = int(uuid.uuid4())
            session['temporary_courses'].append({
                    'id': temp_id,
                    'code': course_code,
                    'name': course_name,
                    'end_date': end_date,
                    'assessments': [],
                    'starting_grade':grade,
                    'starting_marks':total_marks,
                    'grade':grade,
                    'total_marks':total_marks,
                    'goal': goal
            })
        session.modified = True
        if len(session["temporary_courses"])==1:
            flash('signup_prompt', 'info')
        else:
            flash("Course successfully added! Sign up to save your progress.","success")
        return redirect(url_for('dashboard'))
        
    return render_template('add_course.html')

@app.route('/course/<int:course_id>/edit', methods=['POST', 'GET'])
def edit_course(course_id):
    # Check if the user is logged in
    if 'user_id' in session:
        # Fetch the course from the database
        course = Course.query.get_or_404(course_id)
    else:
        # Handle guest user with temporary courses in session
        course = None
        if 'temporary_courses' in session:
            for temp_course in session['temporary_courses']:
                if temp_course['id'] == course_id:
                    course = temp_course
                    break

        if course is None:
            flash("Course not found.", "error")
            return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Extract and update course data from the form
        course_data = {
            'name': request.form.get('course_name'),
            'code': request.form.get('course_code'),
            'end_date': datetime.strptime(request.form.get('end_date'), '%Y-%m-%d'),
            'grade': float(request.form.get('grade')) if request.form.get('grade') else 0.0,
            'total_marks': float(request.form.get('total_marks')) if request.form.get('total_marks') else 0.0,
            'goal': float(request.form.get('goal'))
        }

        if 'user_id' in session:
            # Update course in the database
            for key, value in course_data.items():
                setattr(course, key, value)
            db.session.commit()
        else:
            # Update temporary course in the session
            for key, value in course_data.items():
                course[key] = value
            session.modified = True

        flash("Course successfully updated!", "success")
        return redirect(url_for('course_details', course_id=course_id))

    # If GET request, display the course data for editing
    return render_template('add_course.html', course=course)



@app.route('/course/<course_id>/add_assessment', methods=['POST','GET'])
def add_assessment(course_id):
    if request.method == 'POST':
        # Extract assessment data and the associated course code from the form

        name= request.form.get('name')
        date_str=request.form.get('date')
        date=datetime.strptime(date_str, '%Y-%m-%d')
        earned = float(request.form.get('earned'))
        total= float(request.form.get('total'))
        weight=request.form.get('weight')
        if weight:
            weight=float(weight)/100
      
        if earned>total:
            session['form_data'] = request.form
            flash("Earned cannot be more than Total. Eg. 9/10",'danger')
            return redirect(url_for('add_assessment', course_id=course_id))
        
        if 'user_id' in session:
            # Add the assessment to the database if the user is logged in
            user_id = session['user_id']
            course = Course.query.filter_by(id=course_id,user_id=user_id).first()
                             
            if course:
                new_assessment = Assessment(name=name, date=date, earned=earned,total=total,course_id=course_id)
               
                if not weight:
                    total_earned = (course.grade/100)*course.total_marks
                    # course.total_marks,course.grade=course.get_updated_grade()
                else:
                    percentage=earned/total
                    denom=weight*100
                    new_assessment.total=denom
                    total_weight_earned=percentage*denom
                    new_assessment.earned=total_weight_earned

                db.session.add(new_assessment)
                course.total_marks, course.grade = course.get_updated_grade()
                db.session.commit()
               
           
                
            else:
                flash('Course not found', 'danger')
                return redirect(url_for('dashboard'))  # Or wherever you want to redirect to
        else:  # For guest users
            for course in session['temporary_courses']:
                if str(course['id']) == str(course_id):
                    # Add the assessment to this course
                    temp_id = int(uuid.uuid4())
                    course['assessments'].append({
                        'id':temp_id,
                        'name': name,
                        'date':date,
                        'earned': earned,
                        'total':total,
                    })
                 
                    session.modified = True
                    total_earned = (course['grade']/100)*course['total_marks']
                    course['total_marks'] = course['total_marks'] + total
                    course['grade'] = ((total_earned + earned)/course['total_marks'])*100
                    break

        form_data=session.pop('form_data',None)
   
        return redirect(url_for('course_details', course_id=course_id))
    
    return render_template('add_assesment.html',course_id=course_id)


@app.route('/course/<int:course_id>/update_grade', methods=["POST"])
def update_grade(course_id):
    course=None
    new_grade=int(request.form.get('new_grade'))
    if 'user_id' in session:
        course=Course.query.get(course_id)
        if not course:
            return render_template("not_found.html")
        course.grade=new_grade
      
    else:
        courses=session.get("temporary_courses",[])
        for c in courses:
            if c['id']==course_id:
                c['grade']=new_grade
        if not course:
            return render_template("not_found.html")
    return redirect(url_for('course_details',course_id=course_id))

@app.route('/course/<int:course_id>/delete',methods=["POST"])
def delete_course(course_id):
    if request.form.get('_method') == 'DELETE':
        course=None
        if 'user_id' in session:
            course=Course.query.get(course_id)
            if not course:
                return render_template("not_found.html")
            Assessment.query.filter_by(course_id=course_id).delete()
            db.session.delete(course)
            db.session.commit()

        else:
            courses=session.get('temporary_courses',[])
            courses=[c for c in courses if c["id"]!=course_id]
            session["temporary_courses"]=courses
        flash('Course deleted successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid method', 'error')
        return redirect(url_for('courses_dashboard'))
    
@app.route('/course/<int:course_id>/assessment/<int:assessment_id>/delete',methods=["POST"])
def delete_assessment(course_id, assessment_id):
    if request.form.get('_method') == 'DELETE':
        assessment=None
        if 'user_id' in session:
            assessment=Assessment.query.get(assessment_id)
            if not assessment:
                flash("assessment not found","error")
                return redirect(url_for("course_details",course_id=course_id))
            course=Course.query.get(course_id)
            if not course:
                flash("Course not found","error")
                return render_template("not_found.html")

            
            db.session.delete(assessment)
            course.total_marks, course.grade = course.get_updated_grade()
            db.session.commit()
           
        else:
            courses=session.get('temporary_courses',[])
            course=None
            for c in courses:
                if c["id"]==course_id:
                    course=c
            if not course:
                return render_template("not_found.html")
            assessments=[a for a in course['assessments'] if a['id']!=assessment_id]
            course['assessments']=assessments
        return redirect(url_for('course_details',course_id=course_id))
    else:
        flash('Invalid method', 'error')
        return redirect(url_for('courses_dashboard'))

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
