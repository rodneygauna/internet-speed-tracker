from flask import render_template
from . import db
from .models import SpeedTestResult
from flask import current_app as app


@app.route('/')
def index():
    '''Render the index page with the latest speed test results.'''
    results = SpeedTestResult.query.order_by(
        SpeedTestResult.timestamp.desc()).limit(30).all()
    results.reverse()
    return render_template('index.html', results=results)
