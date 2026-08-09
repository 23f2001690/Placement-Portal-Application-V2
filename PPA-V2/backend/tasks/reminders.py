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


@celery.task(name="backend.tasks.reminders.send_deadline_reminders")
def send_deadline_reminders():
    """Runs daily. Reminds eligible students about drives closing in the next 24 hours that they haven't applied to yet."""
    from backend.models.job_position import JobPosition
    from backend.models.student import Student

    window_start = datetime.utcnow()
    window_end = window_start + timedelta(hours=24)

    closing_soon = JobPosition.query.filter(
        JobPosition.status == "approved",
        JobPosition.application_deadline >= window_start,
        JobPosition.application_deadline <= window_end,
    ).all()

    sent = 0
    for job in closing_soon:
        applied_student_ids = {a.student_id for a in job.applications}
        students = Student.query.filter_by(is_blacklisted=False).all()

        for student in students:
            if student.id in applied_student_ids:
                continue
            if not _is_eligible(student, job):
                continue

            send_email(
                student.user.email,
                f"Deadline approaching - {job.title}",
                f"Hi {student.full_name},\n\n"
                f"The application deadline for {job.title} at {job.company.company_name} "
                f"is {job.application_deadline.strftime('%d %b %Y, %I:%M %p')} - less than 24 hours away.\n\n"
                "Apply now through the placement portal if you're interested.\n\nPlacement Cell",
            )
            sent += 1

    return f"Sent {sent} deadline reminder(s)"


@celery.task(name="backend.tasks.reminders.notify_admin_interview_scheduled")
def notify_admin_interview_scheduled(application_id):
    """Triggered on-demand the moment a company schedules an interview - not part of the daily schedule."""
    from backend.models.user import User

    admin = User.query.filter_by(role="admin").first()
    if not admin:
        return "No admin account found, skipping"

    application = Application.query.get(application_id)
    if not application:
        return "Application not found, skipping"

    student = application.student
    job = application.job_position
    company = job.company

    html = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
      <h3>Interview Scheduled</h3>
      <p>
        Student Name: {student.full_name}<br>
        Branch: {student.branch or '-'}<br>
        Company: {company.company_name}<br>
        Job Title: {job.title}<br>
        Interview Date &amp; Time: {application.interview_datetime.strftime('%d %b %Y, %I:%M %p')}
      </p>
    </body></html>
    """
    send_email(admin.email, f"Interview Scheduled: {student.full_name} - {company.company_name}", html, html=True)
    return f"Notified admin of interview for application {application_id}"


def _is_eligible(student, job):
    """Local copy of the eligibility check, kept self-contained here to avoid importing from routes."""
    if job.min_cgpa and (student.cgpa or 0) < job.min_cgpa:
        return False
    if job.eligible_branches:
        allowed = [b.strip().lower() for b in job.eligible_branches.split(",") if b.strip()]
        if allowed and (student.branch or "").strip().lower() not in allowed:
            return False
    if job.eligible_year and student.year_of_study and job.eligible_year != student.year_of_study:
        return False
    return True