from datetime import datetime, timedelta

from backend.celery_app import celery
from backend.models.application import Application
from backend.tasks.notifications import send_email


@celery.task(name="backend.tasks.reminders.send_interview_reminders")
def send_interview_reminders():
    """Runs daily. Reminds students whose interview falls in the next 24 hours."""
    window_start = datetime.utcnow()
    window_end = window_start + timedelta(hours=24)

    upcoming = Application.query.filter(
        Application.status == "interview",
        Application.interview_datetime >= window_start,
        Application.interview_datetime <= window_end,
    ).all()

    for application in upcoming:
        student = application.student
        job = application.job_position
        send_email(
            student.user.email,
            f"Interview Reminder - {job.title}",
            f"Hi {student.full_name},\n\n"
            f"This is a reminder that your interview for {job.title} at "
            f"{job.company.company_name} is scheduled on "
            f"{application.interview_datetime.strftime('%d %b %Y, %I:%M %p')}.\n\n"
            "Good luck!\nPlacement Cell",
        )

    return f"Sent {len(upcoming)} interview reminder(s)"