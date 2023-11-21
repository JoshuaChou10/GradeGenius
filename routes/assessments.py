from routes.auth import check_course_ownership
from flask import session, request, redirect, url_for, render_template,flash
from helpers import get_guest_grade,check_grade_change,scale_finals

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
        name= request.form.get('name')
        date_str=request.form.get('date')
        date=datetime.strptime(date_str, '%Y-%m-%d')
        earned = float(request.form.get('earned'))
        total= float(request.form.get('total'))
        weight=request.form.get('weight')
        #If final, get weight and percentage grade
        if weight:
            weight=float(weight)/100
            percentage=earned/total
        else:
            weight=None
            
        if earned>total:
            session['form_data'] = request.form
            flash("Earned cannot be more than Total. Eg. 9/10",'danger')
            return redirect(url_for('add_assessment', course_id=course_id))
        
        if 'user_id' in session:
            # Add the assessment to the database if the user is logged in
            course = Course.query.get(course_id)
            prev_grade=course.grade
            # modify total marks of the final assessment so that it will equal to [weight]% of the total course marks
            new_assessment = Assessment(name=name, date=date, earned=earned,original_earned=earned if weight else None, total=total,original_total=total if weight else None, weight=weight, course_id=course_id)
            db.session.add(new_assessment)
            #if normal assessment then include in the course grade. 
            # Don't include final assessment grade in course grade because will be scaled to fit course marks
            if not weight:
                course.total_marks, course.grade = course.get_updated_grade()
            finals=Assessment.query.filter(Assessment.weight!=None,Assessment.course_id==course.id).all()
            finals=get_scaled_finals(course,total,weight,finals)
            course.total_marks, course.grade = course.get_updated_grade()
            db.session.commit()
                    
        else:  # For guest users
            for c in session['temporary_courses']:
                if str(c['id']) == str(course_id):
                    course = c
                    break
            prev_grade=course['grade']
            temp_id = int(uuid.uuid4())
            course['assessments'].append({
                'id': temp_id,
                'name': name,
                'date': date,
                'earned': earned,
                "original_earned":earned if weight else None,
                'total': total,
                "original_total":total if weight else None,
                'weight': weight
            })
            if not weight:
                course["total_marks"], course["grade"] = get_guest_grade(course)
            finals=[a for a in course['assessments'] if a.get('weight') is not None]
            finals=get_scaled_finals(course,total,weight,finals)
            course['total_marks'],course['grade']=get_guest_grade(course)
            session.modified = True

        check_grade_change(course,prev_grade,'added')
        form_data=session.pop('form_data',None)
        return redirect(url_for('course_details', course_id=course_id))
    
    return render_template('add_assessment.html',course_id=course_id,action="Add")




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
            prev_grade=course.grade
            db.session.delete(assessment)
           
            db.session.commit()
           
        else:
            courses=session.get('temporary_courses',[])
            course=None
            for c in courses:
                if c["id"]==course_id:
                    course=c
                    break
            prev_grade=course['grade']
            
            if not course:
                return render_template("not_found.html")
            assessments=[a for a in course['assessments'] if a['id']!=assessment_id]
            course['assessments']=assessments
            course["total_marks"],course["grade"]=get_guest_grade(course)
            session.modified=True
        check_grade_change(course,prev_grade,'deleted')
        return redirect(url_for('course_details',course_id=course_id))
    else:
        flash('Invalid method', 'error')
        return redirect(url_for('courses_dashboard'))
    
    
@app.route('/course/<int:course_id>/assessment/<int:assessment_id>/edit', methods=['POST', 'GET'])
@check_course_ownership
def edit_assessment(course_id,assessment_id):
    # Check if the user is logged in
    if 'user_id' in session:
        course=Course.query.get(course_id)
        prev_grade=course.grade
        assessment= Assessment.query.get(assessment_id)
    else:
        course = None
        if 'temporary_courses' in session:
            for temp_course in session['temporary_courses']:
                if temp_course['id'] == course_id:
                    course = temp_course
                    break
            prev_grade=course['grade']
        if course is None:
            return render_template("not_found.html")
        
        assessment=None
        for a in course['assessments']:
            if a['id']==assessment_id:
                assessment=a
        if assessment is None:
            flash("Assessment not found","error")
            return redirect(url_for("course_details",course_id=course_id))

    if request.method == 'POST':

        assessment_data = {
            'name': request.form.get('name'),
            'date': datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
            'earned': float(request.form.get('earned')) if request.form.get('earned') else 0.0,
            'total': float(request.form.get('total')) if request.form.get('total') else 0.0,
            'weight': float(request.form.get('weight')) if request.form.get('weight') else None
        }
        if assessment_data["weight"]:
            percentage=assessment_data["earned"]/assessment_data["total"]
            denom=assessment_data["weight"]*100
            assessment_data["total"]=denom
            total_weight_earned=percentage*denom
            assessment_data["earned"]=total_weight_earned


        if 'user_id' in session:
            # Update course in the database
           
            for key, value in assessment_data.items():
                setattr(assessment, key, value)
            course.total_marks, course.grade = course.get_updated_grade() # function uses assesments to calculate so update assesment data first
            db.session.commit()
        else:
            for key, value in assessment_data.items():
                assessment[key] = value
            course["total_marks"],course["grade"]=get_guest_grade(course)
            session.modified = True

        check_grade_change(course,prev_grade,'edited')
        
        return redirect(url_for('course_details', course_id=course_id))
    
    # If GET request, display the course data for editing
    return render_template('add_assessment.html', course=course,assessment=assessment, action="Edit")