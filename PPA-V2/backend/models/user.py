from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from backend.extensions import db


class User(db.Model):
    """
    Single table for all three roles (admin / company / student).
    Company and Student have their own profile tables linked back here,
    so login/auth logic stays in one place regardless of role.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / company / student
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company_profile = db.relationship(
        "Company", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    student_profile = db.relationship(
        "Student", backref="user", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"