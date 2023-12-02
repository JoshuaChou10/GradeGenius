from routes.user import check_course_ownership
from flask import session, request, redirect, url_for, render_template,flash,jsonify
from helpers import get_weights
from datetime import datetime
import uuid
from datetime import datetime
from models import Course, Assessment
from app import app
from flask import session
from app import db

#side bar in all templates need courses
@app.context_processor
def inject_courses():
    courses=None
    if 'user_id' in session:
        courses = Course.query.filter_by(user_id=session['user_id']).all()
    else:
        courses=session.get("temporary_courses",[])
    return dict(courses=courses)

@app.route('/course/<int:course_id>')
@check_course_ownership
def course_details(course_id):
    course=None
    time_left = 0
    if 'user_id' in session:
        course = Course.query.get(course_id)
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
    finals_weight,finals_grade,courses_grade=get_weights(course)
    courses_score=f"{round(courses_grade*((1-finals_weight)*100),1)}/{round((1-finals_weight)*100,1)}"
    finals_score=f"{round(finals_grade*finals_weight*100,1)}/{round(finals_weight*100,1)}"
    return render_template('course_details.html', datetime=datetime,course=course,time_left=time_left if time_left>0 else 0,courses_score=courses_score,finals_score=finals_score)


@app.route('/course/create', methods=['POST', 'GET'])
def create_course():
   
    if request.method == 'POST':
        # Extract the course data from the form
        course_name = request.form.get('course_name')
        course_code = request.form.get('course_code')
        course_description=request.form.get('course_description')
        creation_date= datetime.today()
        end_date_str= request.form.get('end_date')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # Assuming end_date is in 'YYYY-MM-DD' format
        grade= request.form.get('grade')
        total_study=float(request.form.get('total_study'))*60 #store in seconds

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
                                description=course_description,
                                name=course_name,
                                creation_date=creation_date,
                                end_date=end_date, 
                                starting_grade=grade,
                                starting_marks=total_marks,
                                grade=grade,
                                total_marks=total_marks,
                                goal=goal,
                                total_study=total_study
                                )

            db.session.add(new_course)
            db.session.commit()
            return redirect(url_for('course_details', course_id=new_course.id))
        # If the user is not logged in, store the course data temporarily in the session
        else:
            
            if 'temporary_courses' not in session:
                session['temporary_courses'] = []
            if len(session['temporary_courses'])>=2:
                flash("signup_prompt","info")
                return redirect(url_for('dashboard'))
            temp_id = int(uuid.uuid4())
            session['temporary_courses'].append({
                    'id': temp_id,
                    'code': course_code,
                    'description':course_description,
                    'name': course_name,
                    "creation_date": creation_date.strftime('%Y-%m-%d'),
                    'end_date': end_date,
                    'assessments': [],
                    'starting_grade':grade,
                    'starting_marks':total_marks,
                    'grade':grade,
                    'total_marks':total_marks,
                    'goal': goal,
                    'total_study':total_study
            })
        session.modified = True
        if len(session["temporary_courses"])==2:
            flash('signup_prompt', 'info')
        else:
            flash("Course successfully added! Sign up to save your progress.","success")
        return redirect(url_for('dashboard'))
    if 'user_id' not in session:
        if len(session['temporary_courses'])>=2:
            flash("Signup to add more courses!","warning")
            flash("signup_prompt","info")
            return redirect(url_for('dashboard'))
    return render_template('add_course.html',action="Add")

@app.route('/course/<int:course_id>/edit', methods=['POST', 'GET'])
@check_course_ownership
def edit_course(course_id):
    # Check if the user is logged in
    if 'user_id' in session:
        # Fetch the course from the database
        course = Course.query.get(course_id)
    else:
        # Handle guest user with temporary courses in session
        course = None
        if 'temporary_courses' in session:
            for temp_course in session['temporary_courses']:
                if temp_course['id'] == course_id:
                    course = temp_course
                    break

        if course is None:
            return render_template("not_found.html")

    if request.method == 'POST':
        # Extract and update course data from the form
        course_data = {
            'name': request.form.get('course_name'),
            'code': request.form.get('course_code'),
            'description':request.form.get('course_description'),
            'end_date': datetime.strptime(request.form.get('end_date'), '%Y-%m-%d'),
            'starting_grade':float(request.form.get('starting_grade')) if request.form.get('starting_grade') else 0.0,
            'starting_marks':float(request.form.get('starting_marks')) if request.form.get('starting_marks') else 0.0,
            'grade': float(request.form.get('grade')) if request.form.get('grade') else 0.0,
            'goal': float(request.form.get('goal')),
            'total_study':(float(request.form.get('total_study'))*60),
            'time_studied':course.time_studied
        }
      

        if 'user_id' in session:
            # Update course in the database
            for key, value in course_data.items():
                setattr(course, key, value)
            db.session.commit()
  
        else:
            # Update temporary course in the session
            #TODO, time studied and total_study not included in guest session
            for key, value in course_data.items():
                course[key] = value
            session.modified = True

        flash("Course successfully updated!", "success")
        return redirect(url_for('course_details', course_id=course_id))

    # If GET request, display the course data for editing
    return render_template('add_course.html', course=course,action="Edit")


@app.route('/course/<int:course_id>/delete',methods=["POST"])
@check_course_ownership
def delete_course(course_id):
    if request.form.get('_method') == 'DELETE':
        course=None
        if 'user_id' in session:
            course=Course.query.get(course_id)
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
    

@app.route('/course/<int:course_id>/update_grade', methods=["POST"])
@check_course_ownership
def update_grade(course_id):
    course=None
    new_grade=int(request.form.get('new_grade'))
    if 'user_id' in session:
        course=Course.query.get(course_id)
        course.grade=new_grade
        db.session.commit()
    else:
        courses=session.get("temporary_courses",[])
        for c in courses:
            if c['id']==course_id:
                c['grade']=new_grade
        if not course:
            return render_template("not_found.html")
    return redirect(url_for('course_details',course_id=course_id))


@app.route('/course/<int:course_id>/update_study_times', methods=['POST'])
@check_course_ownership
def update_study_times(course_id):
    if 'user_id' in session:
        data = request.json
        course = Course.query.get(course_id)
        if course:
            course.time_studied = data['time_studied']
            db.session.commit()
            return '', 204  # No Content response
    else:
        flash("Sign in to start tracking your studying!","info")
        flash("signup_prompt","info")
    return redirect(url_for("course_details",course_id=course_id))


