import asyncio
from .models import SpeedTestResult
from . import scheduler, db
import json
import os
import logging
from flask import current_app

# Configure logging to output to a file in the instance folder
log_file_path = os.path.join(current_app.instance_path, 'scheduler.log')
logging.basicConfig(
    level=logging.INFO,
    filename=log_file_path,  # Log file in the instance folder
    filemode='a',  # Append to the file
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)
logger = logging.getLogger(__name__)


async def run_speedtest():
    '''Run the speedtest command asynchronously and save the results to the database.'''
    server_id = os.getenv('SPEEDTEST_SERVER_ID')
    cmd = ['speedtest', '--json']
    if server_id:
        cmd.extend(['--server', server_id])

    try:
        logger.info("Running speedtest...")
        # Run the speedtest command asynchronously
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        # Log the raw output for debugging
        logger.debug("Speedtest output: %s", stdout.decode().strip())

        # Log stderr for debugging
        if stderr:
            logger.error("Speedtest stderr: %s", stderr.decode().strip())

        # Check if the process completed successfully
        if process.returncode != 0:
            logger.error(
                "Speedtest command failed with return code %d",
                process.returncode)
            return

        # Parse the JSON output
        try:
            data = json.loads(stdout.decode().strip())
        except json.JSONDecodeError as e:
            logger.error("Failed to parse speedtest output as JSON: %s", e)
            logger.debug("Raw output: %s", stdout.decode().strip())
            return

        # Validate required keys in the output
        if 'download' not in data or 'upload' not in data or 'ping' not in data:
            logger.error("Invalid speedtest output: Missing required keys")
            return

        # Convert bandwidth to Mbps (example response is in the JSON is 169762298.676475 and should save as 169.762298676475)
        record = SpeedTestResult(
            download=data['download'] / 1000000,
            upload=data['upload'] / 1000000,
            ping=data['ping'],
            hosted_name=data['server']['sponsor'],
            hosted_location=data['server']['name'],
        )

        # Use a context manager for database operations
        with db.session.begin():
            db.session.add(record)
        logger.info("Speedtest results saved successfully.")
    except Exception as e:
        logger.error("An unexpected error occurred during speedtest: %s", e)


def start_scheduler():
    '''Start the scheduler to run speedtest at regular intervals.'''
    try:
        interval = int(os.getenv('SPEEDTEST_INTERVAL_MINUTES', '30'))

        # Pass the Flask app instance to the scheduler job
        app = current_app._get_current_object()

        # Check if the job already exists
        if scheduler.get_job('speedtest_job') is None:
            scheduler.add_job(
                lambda: run_speedtest_with_app_context(
                    app),  # Pass the app instance
                'interval',
                minutes=interval,
                id='speedtest_job',
                replace_existing=True
            )
            logger.info("Added speedtest job to the scheduler.")
        else:
            logger.info("Speedtest job already exists. Skipping job addition.")

        if not scheduler.running:
            scheduler.start()
            logger.info(
                "Scheduler started with an interval of %d minutes.", interval)
    except Exception as e:
        logger.error("Failed to start scheduler: %s", e)


def run_speedtest_with_app_context(app):
    '''Run the speedtest command within the Flask application context.'''
    with app.app_context():  # Push the app context manually
        asyncio.run(run_speedtest())
