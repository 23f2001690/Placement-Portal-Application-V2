from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from backend.extensions import db
from backend.decorators import role_required
from backend.models.user import User
from backend.models.student import Student
from backend.models.job_position import JobPosition
from backend.models.application import Application
from backend.models.placement import Placement

company_bp = Blueprint("company", __name__, url_prefix="/api/company")


def _current_company():
    user = User.query.get(int(get_jwt_identity()))
    return user.company_profile if user else None


def _is_approved(company):
    return company and company.approval_status == "approved" and not company.is_blacklisted


@company_bp.route("/profile", methods=["GET"])
@role_required("company")
def profile():
    company = _current_company()
    if not company:
        return jsonify(error="Company profile not found"), 404
    return jsonify(_company_json(company)), 200


@company_bp.route("/stats", methods=["GET"])
@role_required("company")
def stats():
    company = _current_company()
    if not company:
        return jsonify(error="Company profile not found"), 404

    job_ids = [j.id for j in company.job_positions]
    total_applications = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    total_shortlisted = Application.query.filter(
        Application.job_id.in_(job_ids), Application.status == "shortlisted"
    ).count() if job_ids else 0

    return jsonify(
        total_job_positions=len(job_ids),
        total_applications=total_applications,
        total_shortlisted=total_shortlisted,
    ), 200


@company_bp.route("/job-positions", methods=["GET"])
@role_required("company")
def list_job_positions():
    company = _current_company()
    jobs = JobPosition.query.filter_by(company_id=company.id).order_by(JobPosition.id.desc()).all()
    return jsonify([_job_json(j) for j in jobs]), 200


@company_bp.route("/job-positions", methods=["POST"])
@role_required("company")
def create_job_position():
    company = _current_company()
    # only approved companies may create drives - enforced here, not just in the UI
    if not _is_approved(company):
        return jsonify(error="Your company must be approved by admin before posting drives"), 403

    data = request.get_json() or {}
    if not data.get("title"):
        return jsonify(error="Job title is required"), 400

    deadline = None
    if data.get("application_deadline"):
        try:
            deadline = datetime.fromisoformat(data["application_deadline"])
        except ValueError:
            return jsonify(error="application_deadline must be a valid date/time"), 400

    job = JobPosition(
        company_id=company.id,
        title=data["title"],
        description=data.get("description"),
        salary=data.get("salary"),
        skills_required=data.get("skills_required"),
        min_cgpa=data.get("min_cgpa") or 0,
        eligible_branches=data.get("eligible_branches"),
        eligible_year=data.get("eligible_year"),
        application_deadline=deadline,
        status="pending",
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(message="Drive submitted for admin approval", job_position=_job_json(job)), 201


@company_bp.route("/job-positions/<int:job_id>/close", methods=["POST"])
@role_required("company")
def close_job_position(job_id):
    company = _current_company()
    job = JobPosition.query.filter_by(id=job_id, company_id=company.id).first_or_404()
    if job.status != "approved":
        return jsonify(error="Only an approved drive can be closed"), 400
    job.status = "closed"
    db.session.commit()
    return jsonify(message="Drive closed", job_position=_job_json(job)), 200


@company_bp.route("/job-positions/<int:job_id>/applications", methods=["GET"])
@role_required("company")
def job_applications(job_id):
    company = _current_company()
    job = JobPosition.query.filter_by(id=job_id, company_id=company.id).first_or_404()
    applications = Application.query.filter_by(job_id=job.id).order_by(Application.id.desc()).all()
    return jsonify([_application_json(a) for a in applications]), 200


@company_bp.route("/applications/<int:application_id>/status", methods=["POST"])
@role_required("company")
def update_application_status(application_id):
    company = _current_company()
    application = Application.query.get_or_404(application_id)

    if application.job_position.company_id != company.id:
        return jsonify(error="This application does not belong to your company"), 403

    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in ("shortlisted", "offer", "placed", "rejected"):
        return jsonify(error="status must be shortlisted, offer, placed or rejected"), 400

    application.status = new_status
    if "feedback" in data:
        application.feedback = data["feedback"]

    if new_status == "placed":
        joining_date = None
        if data.get("joining_date"):
            try:
                joining_date = datetime.fromisoformat(data["joining_date"]).date()
            except ValueError:
                return jsonify(error="joining_date must be a valid date"), 400

        if application.placement:
            application.placement.package_offered = data.get("package_offered") or application.placement.package_offered
            application.placement.joining_date = joining_date or application.placement.joining_date
        else:
            db.session.add(Placement(
                application_id=application.id,
                student_id=application.student_id,
                company_id=company.id,
                position_title=application.job_position.title,
                package_offered=data.get("package_offered") or application.job_position.salary,
                joining_date=joining_date,
            ))

    db.session.commit()
    return jsonify(message="Application updated", application=_application_json(application)), 200


@company_bp.route("/applications/<int:application_id>/schedule-interview", methods=["POST"])
@role_required("company")
def schedule_interview(application_id):
    company = _current_company()
    application = Application.query.get_or_404(application_id)

    if application.job_position.company_id != company.id:
        return jsonify(error="This application does not belong to your company"), 403
    if application.status not in ("shortlisted", "interview"):
        return jsonify(error="Only shortlisted candidates can have an interview scheduled"), 400

    data = request.get_json() or {}
    if not data.get("interview_datetime"):
        return jsonify(error="interview_datetime is required"), 400
    try:
        application.interview_datetime = datetime.fromisoformat(data["interview_datetime"])
    except ValueError:
        return jsonify(error="interview_datetime must be a valid date/time"), 400

    application.status = "interview"
    db.session.commit()
    return jsonify(message="Interview scheduled", application=_application_json(application)), 200


@company_bp.route("/students/<int:student_id>/history", methods=["GET"])
@role_required("company")
def student_history(student_id):
    company = _current_company()
    student = Student.query.get_or_404(student_id)

    # a company may only view students who have actually applied to one of its drives
    applied_here = Application.query.join(JobPosition).filter(
        Application.student_id == student.id, JobPosition.company_id == company.id
    ).first()
    if not applied_here:
        return jsonify(error="You can only view applicants who applied to your drives"), 403

    applications = Application.query.filter_by(student_id=student.id).order_by(Application.id.desc()).all()
    return jsonify(
        profile={"id": student.id, "full_name": student.full_name, "branch": student.branch,
                 "cgpa": student.cgpa, "skills": student.skills, "email": student.user.email},
        applications=[_application_json(a) for a in applications],
    ), 200


def _company_json(c):
    return {
        "id": c.id, "company_name": c.company_name, "industry": c.industry, "location": c.location,
        "website": c.website, "hr_contact": c.hr_contact, "about": c.about,
        "approval_status": c.approval_status, "is_blacklisted": c.is_blacklisted,
    }


def _job_json(j):
    return {
        "id": j.id, "title": j.title, "description": j.description, "salary": j.salary,
        "skills_required": j.skills_required, "min_cgpa": j.min_cgpa,
        "eligible_branches": j.eligible_branches, "eligible_year": j.eligible_year,
        "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
        "status": j.status, "applicant_count": len(j.applications),
    }


def _application_json(a):
    placement = a.placement
    return {
        "id": a.id, "student_id": a.student_id, "student_name": a.student.full_name,
        "student_email": a.student.user.email, "branch": a.student.branch, "cgpa": a.student.cgpa,
        "resume_path": a.student.resume_path, "job_title": a.job_position.title,
        "company_name": a.job_position.company.company_name, "status": a.status, "feedback": a.feedback,
        "interview_datetime": a.interview_datetime.isoformat() if a.interview_datetime else None,
        "applied_on": a.applied_on.isoformat(),
        "package_offered": placement.package_offered if placement else None,
        "joining_date": placement.joining_date.isoformat() if placement and placement.joining_date else None,
    }