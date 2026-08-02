"""
Entry point for the Celery worker and beat scheduler - kept separate from
app.py because Flask (the web server) and Celery (the task runner) are two
different long-running processes that both need the Flask app context.

Run with:
    celery -A backend.celery_worker.celery worker --loglevel=info --pool=solo
    celery -A backend.celery_worker.celery beat --loglevel=info
"""
from backend.app import create_app
from backend.celery_app import init_celery

flask_app = create_app()
celery = init_celery(flask_app)

import backend.tasks.reminders  # noqa: F401,E402
import backend.tasks.reports  # noqa: F401,E402
import backend.tasks.exports  # noqa: F401,E402