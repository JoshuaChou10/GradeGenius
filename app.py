from flask import Flask
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

from models import db  # Import models after defining app
db.init_app(app)  # Initialize db with app
from routes import *
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
