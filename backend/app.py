from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import session
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courses = db.relationship('Course', backref='user', lazy=True)
    GPA = db.Column(db.Float, nullable=True)  # GPA is usually a float, not an integer
    goal = db.Column(db.String(100), nullable=True)  # Goal for the user (could be a description or target GPA)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mark = db.Column(db.Float, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # Foreign key linking to Course

#do course_object.user to get user
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Allow nullable for temporary courses
    temporary = db.Column(db.Boolean, default=True)  # New field to mark temporary courses
    code = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    assessments = db.relationship('Assessment', backref='course', lazy=True)  # Relationship with Assessment
    goal = db.Column(db.String(100), nullable=True)  # Goal for the course (e.g., target grade or outcome)


    # Method to calculate days remaining for the course to end
    def days_remaining(self):
        current_date = datetime.utcnow()
        difference = self.end_date - current_date
        return difference.days if difference.days > 0 else 0  # Return 0 if course has ended

@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

@app.route('/course/<int:course_id>')
def course_details(course_id):
    course = Course.query.get(course_id)
    if not course:
        return redirect(url_for('index'))
    days_left = course.days_remaining()
    return render_template('course_details.html', course=course, days_left=days_left)



# @app.route('/create_course', methods=['POST'])
# def create_course():
#     # ... course creation logic ...

#     user_id = None
#     if 'user_id' in session:  # Check if user is logged in
#         user_id = session['user_id']

#     new_course = Course(name="Example", user_id=user_id, temporary=(user_id is None), ...)
#     db.session.add(new_course)
#     db.session.commit()

#     # If user is not logged in, store course ID in session for later association with user
#     if user_id is None:
#         session['temp_course_id'] = new_course.id

#     return redirect(url_for('index'))

# @app.route('/signup', methods=['POST'])
# def signup():
#     # ... user registration logic ...
#     new_user = User(username="example", ...)
#     db.session.add(new_user)
#     db.session.commit()

#     # If there's a temp_course_id in the session, associate it with the new user
#     if 'temp_course_id' in session:
#         temp_course = Course.query.get(session['temp_course_id'])
#         if temp_course:
#             temp_course.user_id = new_user.id
#             temp_course.temporary = False
#             db.session.commit()
#         # Optionally clear the temp_course_id from the session
#         session.pop('temp_course_id', None)

#     return redirect(url_for('dashboard'))

# @app.route('/login', methods=['POST'])
# def login():
#     # ... authentication logic ...

#     if user_authenticated:  
#         session['user_id'] = user.id  # Store the logged-in user's ID in the session

#     return redirect(url_for('index'))

# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     return redirect(url_for('index'))

# with app.app_context():
#     db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
