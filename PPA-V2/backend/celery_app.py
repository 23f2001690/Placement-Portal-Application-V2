from celery import Celery
from celery.schedules import crontab

from backend.config import Config

celery = Celery(
    "placement_portal",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
)

celery.conf.beat_schedule = {
    "daily-interview-reminders": {
        "task": "backend.tasks.reminders.send_interview_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    "daily-deadline-reminders": {
        "task": "backend.tasks.reminders.send_deadline_reminders",
        "schedule": crontab(hour=8, minute=15),
    },
    "monthly-company-report": {
        "task": "backend.tasks.reports.generate_monthly_report",
        "schedule": crontab(day_of_month=1, hour=7, minute=0),
    },
    "monthly-admin-report": {
        "task": "backend.tasks.reports.generate_admin_monthly_report",
        "schedule": crontab(day_of_month=1, hour=7, minute=5),
    },
}


def init_celery(app):
    """Wraps every task in a Flask app context so db.session works normally inside tasks."""
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery