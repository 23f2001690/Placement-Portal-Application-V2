from datetime import datetime
from backend.extensions import db


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job_positions.id"), nullable=False)

    status = db.Column(db.String(20), default="applied")  # applied / shortlisted / selected / rejected
    feedback = db.Column(db.Text)
    interview_datetime = db.Column(db.DateTime)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)

    placement = db.relationship(
        "Placement", backref="application", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("student_id", "job_id", name="uq_student_job"),
    )

    def __repr__(self):
        return f"<Application student={self.student_id} job={self.job_id} status={self.status}>"