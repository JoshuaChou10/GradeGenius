import os
from flask_session import Session

class Config:
    SECRET_KEY = os.urandom(16).hex()
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SESSION_TYPE = 'filesystem'  # Specifies the type of session interface to use
    SESSION_PERMANENT = False  # If True, makes the session last indefinitely. Default is 31 days
    # SESSION_USE_SIGNER = True  # Helps protect the user's session cookie
    # SESSION_KEY_PREFIX = 'my_app:'  # Prefix for the session cookie name, to avoid conflicts
    # SESSION_FILE_DIR = 'session_data'

