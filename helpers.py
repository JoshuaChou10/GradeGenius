from flask import session

def get_guest_grade(course):
        earned=(course["starting_marks"]*course["starting_grade"])/100
        total_marks=course["starting_marks"]
        for a in course["assessments"]:
            earned+=a["earned"]
            total_marks+=a["total"]
        grade=int((earned/total_marks)*100*100)/100 if total_marks!=0 else 0
        return total_marks,grade


def get_guest_GPA():
    courses = session.get("temporary_courses", [])
    total = 0
    count = 0
    for course in courses:
        if 'grade' in course and course['grade'] != 0.0:
            total += course['grade']
            count += 1

    return total / count if count > 0 else 0


      
      
    