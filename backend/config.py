# config.py

import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:armydec4@localhost/expense_tracker_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")  # For secure sessions

# Example for .env: DATABASE_URL=mysql+pymysql://root:password@localhost/expense_tracker
