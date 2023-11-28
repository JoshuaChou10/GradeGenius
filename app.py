from flask import Flask
from config import Config
from flask_session import Session


app = Flask(__name__)
app.config.from_object(Config)
Session(app)

from models import db  # Import models after defining app
db.init_app(app)  # Initialize db with app
from routes.main_routes import *
from routes.course import *
from routes.assessments import *
from routes.user import *

# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run()
