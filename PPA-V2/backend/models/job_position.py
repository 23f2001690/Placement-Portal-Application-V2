from datetime import datetime
from backend.extensions import db


class JobPosition(db.Model):
    """A placement drive/opening created by a company. Goes live only once admin approves it."""
    __tablename__ = "job_positions"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    salary = db.Column(db.String(50))
    skills_required = db.Column(db.String(300))

    # eligibility criteria checked before a student is allowed to apply
    min_cgpa = db.Column(db.Float, default=0)
    eligible_branches = db.Column(db.String(200))  # comma separated, e.g. "CSE,IT,ECE"
    eligible_year = db.Column(db.Integer)

    application_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="pending")  # pending / approved / rejected / closed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship(
        "Application", backref="job_position", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<JobPosition {self.title}>"