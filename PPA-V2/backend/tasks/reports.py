import calendar
from datetime import datetime, timedelta

from backend.celery_app import celery
from backend.models.company import Company
from backend.models.job_position import JobPosition
from backend.models.application import Application
from backend.models.placement import Placement
from backend.tasks.notifications import send_email


def _previous_month_range(reference=None):
    reference = reference or datetime.utcnow()
    first_of_this_month = reference.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = first_of_this_month - timedelta(seconds=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return last_month_start, last_month_end


@celery.task(name="backend.tasks.reports.generate_monthly_report")
def generate_monthly_report():
    """Runs on the 1st of every month. Emails each approved company a summary of last month's activity."""
    start, end = _previous_month_range()
    month_label = f"{calendar.month_name[start.month]} {start.year}"

    companies = Company.query.filter_by(approval_status="approved").all()
    sent = 0

    for company in companies:
        job_ids = [j.id for j in company.job_positions]

        drives = JobPosition.query.filter(
            JobPosition.company_id == company.id,
            JobPosition.created_at >= start, JobPosition.created_at <= end,
        ).count()

        applications = Application.query.filter(
            Application.job_id.in_(job_ids),
            Application.applied_on >= start, Application.applied_on <= end,
        ).count() if job_ids else 0

        placements = Placement.query.filter(
            Placement.company_id == company.id,
            Placement.recorded_on >= start, Placement.recorded_on <= end,
        ).count()

        html = f"""
        <html><body style="font-family: Arial, sans-serif;">
          <h2>Placement Activity Report - {month_label}</h2>
          <p>Dear {company.company_name} team,</p>
          <p>Here is a summary of your placement drive activity for {month_label}:</p>
          <table border="1" cellpadding="8" cellspacing="0">
            <tr><td><strong>Drives Posted</strong></td><td>{drives}</td></tr>
            <tr><td><strong>Applications Received</strong></td><td>{applications}</td></tr>
            <tr><td><strong>Students Placed</strong></td><td>{placements}</td></tr>
          </table>
          <p>Thank you for partnering with our placement cell.</p>
        </body></html>
        """
        send_email(company.user.email, f"Placement Activity Report - {month_label}", html, html=True)
        sent += 1

    return f"Sent {sent} monthly report(s) for {month_label}"