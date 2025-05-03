from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

db = SQLAlchemy()
scheduler = BackgroundScheduler()


def create_app():
    '''Create and configure the Flask application.'''
    load_dotenv()
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    db.init_app(app)

    with app.app_context():
        from . import routes
        from .scheduling import start_scheduler
        db.create_all()
        start_scheduler()  # Start the scheduler here

    return app
