from flask import Flask, render_template,session, redirect, url_for, request
import uuid
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
    goal = db.Column(db.Integer, nullable=True)  # Goal for the user (could be a description or target GPA)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mark = db.Column(db.Float, nullable=True)
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
    current_grade=db.Column(db.Integer, nullable=False)
    goal = db.Column(db.Integer, nullable=False)  # Goal for the course (e.g., target grade or outcome)


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



#@app.route('/create_course', methods=['POST'])
def create_course():
    # Extract the course data from the form (or wherever it's coming from)
    course_name = request.form.get('course_name')
    course_code = request.form.get('course_code')
    end_date=request.form.get('end_date')
    goal=request.form.get("goal")
    #TODO add if any past assesments

    # If the user is logged in, store the course in the database
    if 'user_id' in session:
        user_id = session['user_id']
        new_course = Course(name=course_name, code=course_code, user_id=user_id)
        db.session.add(new_course)
        db.session.commit()
    # If the user is not logged in, store the course data temporarily in the session
    else:
        if 'temporary_courses' not in session:
            session['temporary_courses'] = []
        temp_id = str(uuid.uuid4())
        session['temporary_courses'].append({
        'id': temp_id,
        'code': course_code,
        'name': course_name,
        'end_date':end_date,
        'assessments': [],
        'goal':goal
    })


    return redirect(url_for('index'))

@app.route('/course/<course_code>/add_assessment', methods=['POST'])
def add_assessment(course_code):
    # Extract assessment data and the associated course code from the form

    assessment_name = request.form.get('assessment_name')
    assessment_mark = request.form.get('assessment_mark')

    if 'user_id' in session:
        # Add the assessment to the database if the user is logged in
        user_id = session['user_id']
        course = Course.query.filter_by(user_id=user_id, code=course_code).first()
        if course:
            new_assessment = Assessment(name=assessment_name, mark=assessment_mark, course_id=course.id)
            db.session.add(new_assessment)
            db.session.commit()
    else:  # For guest users
        for course in session['temporary_courses']:
            if course['id'] == course_code:
                # Add the assessment to this course
                course['assessments'].append({
                    'name': request.form.get('assessment_name'),
                    'mark': request.form.get('assessment_mark')
                })
    return redirect(url_for('course_details', course_id=course_code))



@app.route('/signup', methods=['POST'])
def signup():
    # ... user registration logic ...

    if 'temporary_courses' in session:
        temp_courses_data = session['temporary_courses']
        for course_data in temp_courses_data:
            temp_course = Course(name=course_data['name'], code=course_data['code'], user_id=new_user.id)
            db.session.add(temp_course)
            db.session.flush()  # to get an ID for the new course before committing
            for assessment_data in course_data['assessments']:
                new_assessment = Assessment(name=assessment_data['name'], mark=assessment_data['mark'], course_id=temp_course.id)
                db.session.add(new_assessment)
            db.session.commit()
        session.pop('temporary_courses', None)

    return redirect(url_for('dashboard'))


@app.route('/login', methods=['POST'])
def login():
    # ... authentication logic ...

    # Let's assume the user was successfully authenticated and is stored in the variable `user`
    if user_authenticated:  
        session['user_id'] = user.id  # Store the logged-in user's ID in the session

    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))
# with app.app_context():
#     db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
