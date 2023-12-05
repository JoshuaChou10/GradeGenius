from flask import Flask
from config import Config
from flask_session import Session
from apscheduler.schedulers.background import BackgroundScheduler
import atexit  # Import the atexit module
# from flask_talisman import Talisman

app = Flask(__name__)

app.config.from_object(Config)
# TODO Enforce HTTPS for production, will not allow user to access if not https

# talisman = Talisman(app)
Session(app)

from models import db  # Import models after defining app
db.init_app(app)  # Initialize db with app
from routes.main_routes import *
from routes.course import *
from routes.assessments import *
from routes.user import *
with app.app_context():
    db.create_all()
def reset_study_times(app):
   
        courses = Course.query.all()
        for course in courses:
            course.time_studied = 0
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=reset_study_times, args=[app], trigger='cron', hour=0, minute=0)


# Start the scheduler
scheduler.start()


atexit.register(lambda: scheduler.shutdown(wait=False))


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        app.run()
