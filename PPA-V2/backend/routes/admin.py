from flask import Blueprint, request, jsonify
from sqlalchemy import or_

from backend.extensions import db
from backend.decorators import role_required
from backend.models.company import Company
from backend.models.student import Student
from backend.models.job_position import JobPosition
from backend.models.application import Application
from backend.models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/stats", methods=["GET"])
@role_required("admin")
def stats():
    return jsonify(
        total_students=Student.query.count(),
        total_companies=Company.query.count(),
        total_job_positions=JobPosition.query.count(),
        total_applications=Application.query.count(),
    ), 200


# ---------- Companies ----------

@admin_bp.route("/companies", methods=["GET"])
@role_required("admin")
def list_companies():
    search = request.args.get("search", "").strip()
    query = Company.query
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Company.company_name.ilike(like), Company.industry.ilike(like)))
    companies = query.order_by(Company.id).all()
    return jsonify([_company_json(c) for c in companies]), 200


@admin_bp.route("/companies/<int:company_id>/approve", methods=["POST"])
@role_required("admin")
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = "approved"
    db.session.commit()
    return jsonify(message="Company approved", company=_company_json(company)), 200


@admin_bp.route("/companies/<int:company_id>/reject", methods=["POST"])
@role_required("admin")
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = "rejected"
    db.session.commit()
    return jsonify(message="Company rejected", company=_company_json(company)), 200


@admin_bp.route("/companies/<int:company_id>", methods=["DELETE"])
@role_required("admin")
def remove_company(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company.user)  # cascades: company -> job positions -> applications -> placements
    db.session.commit()
    return jsonify(message="Company removed"), 200


@admin_bp.route("/companies/<int:company_id>/blacklist", methods=["POST"])
@role_required("admin")
def toggle_company_blacklist(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    company.user.is_active = not company.is_blacklisted
    db.session.commit()
    return jsonify(message="Updated", company=_company_json(company)), 200


# ---------- Students ----------

@admin_bp.route("/students", methods=["GET"])
@role_required("admin")
def list_students():
    search = request.args.get("search", "").strip()
    query = Student.query.join(User, Student.user_id == User.id)
    if search:
        like = f"%{search}%"
        filters = [Student.full_name.ilike(like), User.email.ilike(like)]
        if search.isdigit():
            filters.append(Student.id == int(search))
        query = query.filter(or_(*filters))
    students = query.order_by(Student.id).all()
    return jsonify([_student_json(s) for s in students]), 200


@admin_bp.route("/students/<int:student_id>", methods=["DELETE"])
@role_required("admin")
def remove_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student.user)  # cascades: student -> applications -> placements
    db.session.commit()
    return jsonify(message="Student removed"), 200


@admin_bp.route("/students/<int:student_id>/blacklist", methods=["POST"])
@role_required("admin")
def toggle_student_blacklist(student_id):
    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = not student.is_blacklisted
    student.user.is_active = not student.is_blacklisted
    db.session.commit()
    return jsonify(message="Updated", student=_student_json(student)), 200


# ---------- Job Postings / Placement Drives ----------

@admin_bp.route("/job-positions", methods=["GET"])
@role_required("admin")
def list_job_positions():
    status = request.args.get("status")
    query = JobPosition.query
    if status:
        query = query.filter_by(status=status)
    jobs = query.order_by(JobPosition.id.desc()).all()
    return jsonify([_job_json(j) for j in jobs]), 200


@admin_bp.route("/job-positions/<int:job_id>/approve", methods=["POST"])
@role_required("admin")
def approve_job(job_id):
    job = JobPosition.query.get_or_404(job_id)
    job.status = "approved"
    db.session.commit()
    return jsonify(message="Drive approved", job_position=_job_json(job)), 200


@admin_bp.route("/job-positions/<int:job_id>/reject", methods=["POST"])
@role_required("admin")
def reject_job(job_id):
    job = JobPosition.query.get_or_404(job_id)
    job.status = "rejected"
    db.session.commit()
    return jsonify(message="Drive rejected", job_position=_job_json(job)), 200


@admin_bp.route("/job-positions/<int:job_id>", methods=["DELETE"])
@role_required("admin")
def remove_job(job_id):
    job = JobPosition.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify(message="Job posting removed"), 200


# ---------- Applications ----------

@admin_bp.route("/applications", methods=["GET"])
@role_required("admin")
def list_applications():
    applications = Application.query.order_by(Application.id.desc()).all()
    return jsonify([_application_json(a) for a in applications]), 200


# ---------- JSON helpers ----------

def _company_json(c):
    return {
        "id": c.id,
        "company_name": c.company_name,
        "industry": c.industry,
        "location": c.location,
        "hr_contact": c.hr_contact,
        "email": c.user.email,
        "approval_status": c.approval_status,
        "is_blacklisted": c.is_blacklisted,
    }


def _student_json(s):
    return {
        "id": s.id,
        "full_name": s.full_name,
        "branch": s.branch,
        "year_of_study": s.year_of_study,
        "cgpa": s.cgpa,
        "email": s.user.email,
        "is_blacklisted": s.is_blacklisted,
    }


def _job_json(j):
    return {
        "id": j.id,
        "title": j.title,
        "company_name": j.company.company_name,
        "salary": j.salary,
        "status": j.status,
        "applicant_count": len(j.applications),
        "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
    }


def _application_json(a):
    return {
        "id": a.id,
        "student_name": a.student.full_name,
        "job_title": a.job_position.title,
        "company_name": a.job_position.company.company_name,
        "status": a.status,
        "applied_on": a.applied_on.isoformat(),
    }