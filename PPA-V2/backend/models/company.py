from backend.extensions import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    company_name = db.Column(db.String(120), nullable=False)
    industry = db.Column(db.String(80))
    location = db.Column(db.String(120))
    website = db.Column(db.String(200))
    hr_contact = db.Column(db.String(120))
    about = db.Column(db.Text)

    approval_status = db.Column(db.String(20), default="pending")  # pending / approved / rejected
    is_blacklisted = db.Column(db.Boolean, default=False)

    job_positions = db.relationship(
        "JobPosition", backref="company", cascade="all, delete-orphan"
    )
    placements = db.relationship("Placement", backref="company")

    def __repr__(self):
        return f"<Company {self.company_name}>"