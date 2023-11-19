from flask import session,flash

def get_guest_grade(course):
        earned=(course["starting_marks"]*course["starting_grade"])/100
        total_marks=course["starting_marks"]
        for a in course["assessments"]:
            earned+=a["earned"]
            total_marks+=a["total"]
        grade=(earned/total_marks)*100 if total_marks!=0 else 0
        return round(total_marks,1),round(grade,1)


def get_guest_GPA():
    courses = session.get("temporary_courses", [])
    total = 0
    count = 0
    for course in courses:
        if 'grade' in course and course['grade'] != 0.0:
            total += course['grade']
            count += 1

    return total / count if count > 0 else 0

def check_grade_change(course,prev_grade,action):
    if prev_grade!=course['grade']:
        flash(f"Assessment succesfully {action}. Grade {'increased' if course['grade']>prev_grade else 'decreased' } from {prev_grade}% to {course['grade']}%")
    else:
        flash(f"Assessment succesfully {action}. Grade stayed the same")


      
      
    