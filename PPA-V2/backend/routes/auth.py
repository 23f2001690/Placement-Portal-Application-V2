from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student
from backend.models.company import Company

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json() or {}
    missing = [f for f in ("email", "password", "full_name") if not data.get(f)]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify(error="Email already registered"), 409

    user = User(email=data["email"], role="student")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()  # so user.id is available before commit

    student = Student(
        user_id=user.id,
        full_name=data["full_name"],
        branch=data.get("branch"),
        year_of_study=data.get("year_of_study"),
        cgpa=data.get("cgpa"),
        skills=data.get("skills"),
    )
    db.session.add(student)
    db.session.commit()

    return jsonify(message="Registration successful, please log in"), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json() or {}
    missing = [f for f in ("email", "password", "company_name") if not data.get(f)]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify(error="Email already registered"), 409

    user = User(email=data["email"], role="company")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()

    company = Company(
        user_id=user.id,
        company_name=data["company_name"],
        industry=data.get("industry"),
        location=data.get("location"),
        website=data.get("website"),
        hr_contact=data.get("hr_contact"),
        about=data.get("about"),
    )
    db.session.add(company)
    db.session.commit()

    return jsonify(message="Registration successful. Your company is pending admin approval."), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not user.check_password(data.get("password", "")):
        return jsonify(error="Invalid email or password"), 401

    if not user.is_active:
        return jsonify(error="This account has been deactivated. Contact the placement cell."), 403

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify(access_token=token, role=user.role, profile=_profile_summary(user)), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify(error="User not found"), 404
    return jsonify(role=user.role, profile=_profile_summary(user)), 200


def _profile_summary(user):
    if user.role == "student" and user.student_profile:
        return {"id": user.student_profile.id, "name": user.student_profile.full_name}
    if user.role == "company" and user.company_profile:
        return {
            "id": user.company_profile.id,
            "name": user.company_profile.company_name,
            "approval_status": user.company_profile.approval_status,
        }
    if user.role == "admin":
        return {"name": "Admin"}
    return {}