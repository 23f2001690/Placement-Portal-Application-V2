from datetime import datetime
from backend.extensions import db


class Placement(db.Model):
    """
    Created once an application's status becomes 'selected'.
    Keeps a permanent placement history record separate from the application
    itself, so offer details (package, joining date) don't clutter Application.
    """
    __tablename__ = "placements"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False, unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    position_title = db.Column(db.String(120))
    package_offered = db.Column(db.String(50))
    joining_date = db.Column(db.Date)
    recorded_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Placement student={self.student_id} company={self.company_id}>"