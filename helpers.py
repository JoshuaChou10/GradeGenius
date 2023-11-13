
def get_guest_grade(course):
        earned=(course["starting_marks"]*course["starting_grade"])/100
        total_marks=course["starting_marks"]
        for a in course["assessments"]:
            earned+=a["earned"]
            total_marks+=a["total"]
        grade=int((earned/total_marks)*100*100)/100 if total_marks!=0 else 0
        return total_marks,grade
    