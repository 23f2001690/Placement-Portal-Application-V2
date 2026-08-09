import re
import calendar
from datetime import datetime, timedelta

from backend.celery_app import celery
from backend.models.company import Company
from backend.models.job_position import JobPosition
from backend.models.application import Application
from backend.models.placement import Placement
from backend.tasks.notifications import send_email


def _parse_salary(value):
    """Pulls a rough numeric value out of a free-text salary string like '10 LPA' or 'Rs. 1,000,000'."""
    if not value:
        return None
    digits = re.sub(r"[^\d.]", "", value)
    if not digits:
        return None
    try:
        return float(digits)
    except ValueError:
        return None


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


@celery.task(name="backend.tasks.reports.generate_admin_monthly_report")
def generate_admin_monthly_report():
    """Runs on the 1st of every month (or on demand via the admin dashboard button)."""
    from backend.models.user import User

    start, end = _previous_month_range()
    month_label = f"{calendar.month_name[start.month]} {start.year}"
    generated_on = datetime.utcnow().strftime("%d %b %Y")

    admin = User.query.filter_by(role="admin").first()
    if not admin:
        return "No admin account found, skipping"

    applications_this_month = Application.query.filter(
        Application.applied_on >= start, Application.applied_on <= end,
    ).all()

    total_received = len(applications_this_month)
    total_rejected = sum(1 for a in applications_this_month if a.status == "rejected")
    total_offer_accepted = sum(1 for a in applications_this_month if a.status == "placed")

    placements_this_month = Placement.query.filter(
        Placement.recorded_on >= start, Placement.recorded_on <= end,
    ).all()

    total_placements = len(placements_this_month)
    salaries = [s for s in (_parse_salary(p.package_offered) for p in placements_this_month) if s is not None]
    avg_salary = f"Rs. {int(sum(salaries) / len(salaries)):,}" if salaries else "N/A"

    placed_rows = "".join(
        f"<li>{p.student.full_name} | {p.student.branch or '-'} | "
        f"{p.package_offered or '-'} | Joining: {p.joining_date.strftime('%d %b %Y') if p.joining_date else '-'}</li>"
        for p in placements_this_month
    )
    if not placed_rows:
        placed_rows = "<li>No students placed this month.</li>"

    html = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
      <h2 style="text-align:center;">Institute Placement Cell</h2>
      <h3 style="text-align:center; font-weight: normal;">Monthly Placement Report - {month_label}</h3>
      <p>Report generated: {generated_on}</p>

      <h4>Application Summary</h4>
      <p>
        Total Applications Received: {total_received}<br>
        Rejected: {total_rejected}<br>
        Offer Accepted: {total_offer_accepted}
      </p>

      <h4>Placement Summary</h4>
      <p>
        Total Placements: {total_placements}<br>
        Average Salary: {avg_salary}
      </p>

      <h4>Placed Students:</h4>
      <ul>
        {placed_rows}
      </ul>
    </body></html>
    """
    send_email(admin.email, f"Admin Report: {month_label}", html, html=True)
    return f"Sent admin report for {month_label}"