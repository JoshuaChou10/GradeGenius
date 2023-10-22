from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courses = db.relationship('Course', backref='user', lazy=True)
    GPA = db.Column(db.Float, nullable=True)  # GPA is usually a float, not an integer
    goal = db.Column(db.Integer, nullable=True)  # Goal for the user (could be a description or target GPA)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    earned = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=True)
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
    grade=db.Column(db.Float, nullable=False)
    total_marks=db.Column(db.Float, nullable=False)
    goal = db.Column(db.Integer, nullable=False)  # Goal for the course (e.g., target grade or outcome)
    def days_remaining(self):
        current_date = datetime.utcnow()
        difference = self.end_date - current_date
        return difference.days if difference.days > 0 else 0  # Return 0 if course has ended
    def update_mark(self,earned,total):
        total_earned = (self.grade/100)*self.total_marks
        self.total_marks = self.total_marks + total
        self.grade = ((total_earned + earned)/self.total_marks)*100
