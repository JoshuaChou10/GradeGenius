from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()
class User(db.Model):
    username=db.Column(db.String, nullable=False)
    password=db.Column(db.String,nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    courses = db.relationship('Course', backref='user', lazy=True)
    GPA = db.Column(db.Float, nullable=True)  # GPA is usually a float, not an integer
    goal = db.Column(db.Integer, nullable=True)  # Goal for the user (could be a description or target GPA)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    earned = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    weight=db.Column(db.Float, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # Foreign key linking to Course

#do course_object.user to get user
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Allow nullable for temporary courses
    code = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    # description = db.Column(db.Text, nullable=True)
    # date_created = db.Column(db.DateTime, default=datetime.utcnow)
    assessments = db.relationship('Assessment', backref='course', lazy=True)  # Relationship with Assessment
    starting_grade=db.Column(db.Float, nullable=False)
    starting_marks=db.Column(db.Float, nullable=False)
    grade=db.Column(db.Float, nullable=False)
    total_marks=db.Column(db.Float, nullable=False)
    goal = db.Column(db.Integer, nullable=False)  # Goal for the course (e.g., target grade or outcome)
    def days_remaining(self):
        current_date = datetime.utcnow()
        difference = self.end_date - current_date
        return difference.days if difference.days > 0 else 0  # Return 0 if course has ended
    def get_updated_grade(self):
        assessments=Assessment.query.filter_by(course_id=self.id).all()
        earned=(self.starting_marks*self.starting_grade)/100
        total_marks=self.starting_marks
        for a in assessments:
            earned+=a.earned
            total_marks+=a.total
        grade=(earned/total_marks)*100 if total_marks!=0 else 0

        return total_marks,grade

        
        
 
  

