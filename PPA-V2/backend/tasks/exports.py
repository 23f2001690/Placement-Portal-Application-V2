import csv
import os
import uuid

from backend.celery_app import celery
from backend.config import Config
from backend.models.student import Student
from backend.models.company import Company
from backend.models.application import Application

os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)


@celery.task(name="backend.tasks.exports.export_student_applications")
def export_student_applications(student_id):
    student = Student.query.get(student_id)
    if not student:
        return {"error": "Student not found"}

    filename = f"student_{student_id}_applications_{uuid.uuid4().hex[:8]}.csv"
    filepath = os.path.join(Config.EXPORT_FOLDER, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Student ID", "Company Name", "Drive Title", "Application Status", "Applied On", "Joining Date"])
        for application in student.applications:
            placement = application.placement
            writer.writerow([
                student.id,
                application.job_position.company.company_name,
                application.job_position.title,
                application.status,
                application.applied_on.strftime("%Y-%m-%d"),
                placement.joining_date.strftime("%Y-%m-%d") if placement and placement.joining_date else "",
            ])

    return {"filename": filename}


@celery.task(name="backend.tasks.exports.export_company_applications")
def export_company_applications(company_id):
    company = Company.query.get(company_id)
    if not company:
        return {"error": "Company not found"}

    job_ids = [j.id for j in company.job_positions]
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all() if job_ids else []

    filename = f"company_{company_id}_applications_{uuid.uuid4().hex[:8]}.csv"
    filepath = os.path.join(Config.EXPORT_FOLDER, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Student Name", "Student Email", "Drive Title", "Application Status", "Applied On", "Package Offered"])
        for application in applications:
            placement = application.placement
            writer.writerow([
                application.student.full_name,
                application.student.user.email,
                application.job_position.title,
                application.status,
                application.applied_on.strftime("%Y-%m-%d"),
                placement.package_offered if placement else "",
            ])

    return {"filename": filename}