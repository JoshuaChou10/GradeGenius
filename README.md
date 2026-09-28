# GradeGenius

GradeGenius is a web app that helps students track their courses, grades, assessments, and study progress. 

## Features

- Add and manage courses
- Track assignments, tests, and exams
- Automatically calculate course grades with weights
- Set target grades for each course
- Track study time and study goals with a study timer
- View CGPA across courses
- Upload and manage course notes
- Share notes with the community in the community section
- Create an account to save progress
- There is also an option for Guest mode for trying the app without signing up

## Tech Stack

- Python
- Flask
- SQLAlchemy
- SQLite
- Jinja2
- HTML/CSS
- Bootstrap
- Flask-Bcrypt
- Flask-Session

## User Flow

1. Add a course with your current grade and target grade
2. Add assessments 
3. The app automatically updates your course grade
4. Track how much time you study for each course
5. View your overall progress from the dashboard

## Running Locally

```bash
git clone https://github.com/JoshuaChou10/GradeGenius.git
cd GradeGenius

python -m venv venv

source venv/bin/activate
# On Windows:
# venv\Scripts\activate

pip install -r requirements.txt

python app.py
```
Open
```
http://127.0.0.1:5000
```
