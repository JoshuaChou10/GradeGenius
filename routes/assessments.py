from routes.auth import check_course_ownership
from flask import session, request, redirect, url_for, render_template,flash


import uuid
from datetime import datetime
from models import Course, Assessment
from app import app
from flask import session
from app import db
@app.route('/course/<course_id>/add_assessment', methods=['POST','GET'])
@check_course_ownership
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

            course = Course.query.get(course_id)
                             
            
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




@app.route('/course/<int:course_id>/assessment/<int:assessment_id>/delete',methods=["POST"])
@check_course_ownership
def delete_assessment(course_id, assessment_id):
    if request.form.get('_method') == 'DELETE':
        assessment=None
        if 'user_id' in session:
            assessment=Assessment.query.get(assessment_id)
            if not assessment:
                flash("assessment not found","error")
                return redirect(url_for("course_details",course_id=course_id))
            course=Course.query.get(course_id)

            
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
    
@app.route('/course/<int:course_id>/assessment/<int:assessment_id>/edit',methods=["POST","GET"])
@check_course_ownership
def edit_assessment(course_id, assessment_id):
    if request.form.get('_method') == 'DELETE':
        assessment=None
        if 'user_id' in session:
            assessment=Assessment.query.get(assessment_id)
            if not assessment:
                flash("assessment not found","error")
                return redirect(url_for("course_details",course_id=course_id))
            course=Course.query.get(course_id)

            
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