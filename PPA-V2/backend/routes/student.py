import os
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
from werkzeug.utils import secure_filename
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_

from backend.extensions import db
from backend.decorators import role_required
from backend.models.user import User
from backend.models.job_position import JobPosition
from backend.models.application import Application

student_bp = Blueprint("student", __name__, url_prefix="/api/student")

RESUME_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "resumes")
os.makedirs(RESUME_FOLDER, exist_ok=True)


def _current_student():
    user = User.query.get(int(get_jwt_identity()))
    return user.student_profile if user else None


@student_bp.route("/profile", methods=["GET"])
@role_required("student")
def profile():
    student = _current_student()
    if not student:
        return jsonify(error="Student profile not found"), 404
    return jsonify(_student_json(student)), 200


@student_bp.route("/profile", methods=["PUT"])
@role_required("student")
def update_profile():
    student = _current_student()
    data = request.get_json() or {}

    for field in ("full_name", "branch", "skills", "experience"):
        if field in data:
            setattr(student, field, data[field])
    if "year_of_study" in data:
        student.year_of_study = data["year_of_study"]
    if "cgpa" in data:
        student.cgpa = data["cgpa"]

    db.session.commit()
    return jsonify(message="Profile updated", profile=_student_json(student)), 200


@student_bp.route("/resume", methods=["POST"])
@role_required("student")
def upload_resume():
    student = _current_student()
    if "resume" not in request.files:
        return jsonify(error="No file uploaded, expected field name 'resume'"), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify(error="No file selected"), 400

    filename = secure_filename(f"student_{student.id}_{file.filename}")
    file.save(os.path.join(RESUME_FOLDER, filename))
    student.resume_path = filename
    db.session.commit()

    return jsonify(message="Resume uploaded", resume_path=filename), 200


@student_bp.route("/job-positions", methods=["GET"])
@role_required("student")
def list_job_positions():
    search = request.args.get("search", "").strip()
    query = JobPosition.query.filter(JobPosition.status.in_(["approved", "closed"]))
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(JobPosition.title.ilike(like), JobPosition.skills_required.ilike(like))
        )
    jobs = query.order_by(JobPosition.id.desc()).all()

    student = _current_student()
    applied_job_ids = {a.job_id for a in student.applications}

    return jsonify([_job_json(j, student, applied_job_ids) for j in jobs]), 200


@student_bp.route("/job-positions/<int:job_id>/apply", methods=["POST"])
@role_required("student")
def apply_to_job(job_id):
    student = _current_student()
    if student.is_blacklisted:
        return jsonify(error="Blacklisted students cannot apply to drives"), 403

    job = JobPosition.query.get_or_404(job_id)

    if job.status != "approved":
        return jsonify(error="This drive is not open for applications"), 400
    if job.application_deadline and job.application_deadline < datetime.utcnow():
        return jsonify(error="Application deadline has passed"), 400

    eligible, reason = _check_eligibility(student, job)
    if not eligible:
        return jsonify(error=reason), 400

    if Application.query.filter_by(student_id=student.id, job_id=job.id).first():
        return jsonify(error="You have already applied to this drive"), 409

    application = Application(student_id=student.id, job_id=job.id)
    db.session.add(application)
    db.session.commit()

    return jsonify(message="Application submitted", application=_application_json(application)), 201


@student_bp.route("/applications", methods=["GET"])
@role_required("student")
def list_applications():
    student = _current_student()
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.id.desc()).all()
    return jsonify([_application_json(a) for a in applications]), 200


@student_bp.route("/applications/<int:application_id>/offer-letter", methods=["GET"])
@role_required("student")
def offer_letter(application_id):
    student = _current_student()
    application = Application.query.get_or_404(application_id)

    if application.student_id != student.id:
        return jsonify(error="This application does not belong to you"), 403
    if application.status != "placed" or not application.placement:
        return jsonify(error="Offer letter is only available once your placement is confirmed"), 400

    placement = application.placement
    company_name = application.job_position.company.company_name

    text = (
        "PLACEMENT OFFER LETTER\n"
        "=======================\n\n"
        f"Student Name : {student.full_name}\n"
        f"Company      : {company_name}\n"
        f"Position     : {placement.position_title}\n"
        f"Package      : {placement.package_offered or 'Not specified'}\n"
        f"Recorded On  : {placement.recorded_on.strftime('%d %B %Y')}\n\n"
        "Congratulations on your placement. This letter confirms your selection "
        f"for the position of {placement.position_title} at {company_name} "
        "through the institute placement portal.\n"
    )

    return Response(
        text,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename=offer_letter_{application.id}.txt"},
    )


def _check_eligibility(student, job):
    if job.min_cgpa and (student.cgpa or 0) < job.min_cgpa:
        return False, f"This drive requires a minimum CGPA of {job.min_cgpa}"
    if job.eligible_branches:
        allowed = [b.strip().lower() for b in job.eligible_branches.split(",") if b.strip()]
        if allowed and (student.branch or "").strip().lower() not in allowed:
            return False, "Your branch is not eligible for this drive"
    if job.eligible_year and student.year_of_study and job.eligible_year != student.year_of_study:
        return False, f"This drive is open only to year {job.eligible_year} students"
    return True, None


def _student_json(s):
    return {
        "id": s.id,
        "full_name": s.full_name,
        "branch": s.branch,
        "year_of_study": s.year_of_study,
        "cgpa": s.cgpa,
        "skills": s.skills,
        "experience": s.experience,
        "resume_path": s.resume_path,
        "email": s.user.email,
    }


def _job_json(j, student, applied_job_ids):
    eligible, reason = _check_eligibility(student, j)
    return {
        "id": j.id,
        "title": j.title,
        "description": j.description,
        "company_name": j.company.company_name,
        "salary": j.salary,
        "skills_required": j.skills_required,
        "min_cgpa": j.min_cgpa,
        "eligible_branches": j.eligible_branches,
        "eligible_year": j.eligible_year,
        "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
        "status": j.status,
        "already_applied": j.id in applied_job_ids,
        "is_eligible": eligible,
        "eligibility_reason": reason,
    }


def _application_json(a):
    return {
        "id": a.id,
        "job_id": a.job_id,
        "job_title": a.job_position.title,
        "company_name": a.job_position.company.company_name,
        "status": a.status,
        "feedback": a.feedback,
        "interview_datetime": a.interview_datetime.isoformat() if a.interview_datetime else None,
        "applied_on": a.applied_on.isoformat(),
    }