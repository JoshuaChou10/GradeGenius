from flask import session,flash
from models import Assessment

def get_attr(obj, attr, default=None):
    if isinstance(obj, dict):
        return obj.get(attr, default)
    else:
        return getattr(obj, attr, default)

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
def get_guest_total_study():
    courses = session.get("temporary_courses",[])
    total=0
    for c in courses:
            total+=c['total_study']
    return total

def check_grade_change(course, prev_grade, action):
    course_grade = get_attr(course, 'grade')
    if prev_grade != course_grade:
        flash(f"Assessment successfully {action}. Grade {'increased' if course_grade > prev_grade else 'decreased'} from {prev_grade}% to {course_grade}%",'info' if prev_grade>course_grade else 'success')
    else:
        flash(f"Assessment successfully {action}. Grade stayed the same",'info')

def get_weights(course):
      #current final should be added before this is called
    finals_weight = 0
    finals_grade = 0
    courses_grade = 0
    if 'user_id' in session:
        finals = Assessment.query.filter(Assessment.weight != None, Assessment.course_id == course.id).all()
        courses = Assessment.query.filter(Assessment.weight == None, Assessment.course_id == course.id).all()
    else:
        assessments = get_attr(course, 'assessments', [])
        finals = [a for a in assessments if get_attr(a, 'weight') is not None]
        courses = [a for a in assessments if get_attr(a, 'weight') is None]
    finals_total=(sum(get_attr(f, 'total') for f in finals)) 
    if len(finals) > 0 and finals_total>0:
        finals_weight = sum(get_attr(f, 'weight') for f in finals)/finals_total
        finals_grade = (sum(get_attr(f, 'earned') for f in finals)) /finals_total

    courses_grade=0 if (get_attr(course,'total_marks')- finals_total)<=0 else ( (sum(get_attr(c, 'earned') for c in courses)+(get_attr(course,'starting_marks')*get_attr(course,'starting_grade')/100) ) /( (sum(get_attr(c, 'total') for c in courses))+get_attr(course,'starting_marks')))
    return finals_weight, finals_grade, courses_grade

   
def scale_finals(course,finals):
    #current final should be added before this is called
    finals_total=sum(get_attr(f,'total') for f in finals) 
    if len(finals)>0:
        finals_weight=sum(get_attr(f,'weight') for f in finals) 
        # if finals_weight>1 or finals_weight>=1 and get_attr(course,'total_marks')-finals_total>0:
        #     return False
                #Get total marks finals are worth eg. 30% finals would be worth 30 marks if weight of course work is 70
        finals_mark=(get_attr(course,'total_marks')-finals_total)/((1/(finals_weight))-1)#Derived from finals_weight=(finals_mark/finals_mark+course_work_marks) 
                #scale each final assessment based on their weighting in the finals, eg. 10% final out of a total of 30% finals
        for f in finals:
            percentage=get_attr(f,'earned')/get_attr(f,'total')
            if 'user_id' in session:
                f.total=round(finals_mark*(get_attr(f,'weight')/finals_weight),1)
                f.earned=round(percentage*get_attr(f,'total'),1)         
            else:
                f['total']=round((finals_mark*f['weight']/finals_weight),1)
                f['earned']=round(percentage*f['total'],1)  
    # return True

               
#TODO Scale finals bool in course.py edit
def handle_grades(course):
    finals=Assessment.query.filter(Assessment.weight!=None,Assessment.course_id==course.id).all() if 'user_id' in session else [a for a in course['assessments'] if a['weight'] is not None]
   
    if 'user_id' in session:
        course.total_marks, course.grade = course.get_updated_grade()
    else:
         course["total_marks"],course["grade"]=get_guest_grade(course)
    before_final=get_attr(course,'total_marks')-(sum(get_attr(f,'total') for f in finals) )
    
    #if no course marks, then dont scale final to 0/0, maintain the score user entered instead
    if before_final>0:
        scale_finals(course,finals)
        if 'user_id' in session:
            course.total_marks, course.grade = course.get_updated_grade()
        else:
            course["total_marks"],course["grade"]=get_guest_grade(course)
