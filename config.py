import os

class Config:
    SECRET_KEY = os.urandom(16).hex()
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
