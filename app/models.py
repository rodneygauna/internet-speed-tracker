from . import db
from datetime import datetime


class SpeedTestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    hosted_name = db.Column(db.Text)
    hosted_location = db.Column(db.Text)
    download = db.Column(db.Float)
    upload = db.Column(db.Float)
    ping = db.Column(db.Float)
