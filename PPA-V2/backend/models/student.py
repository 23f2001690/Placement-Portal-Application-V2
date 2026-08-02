from backend.extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    full_name = db.Column(db.String(120), nullable=False)
    branch = db.Column(db.String(80))
    year_of_study = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    skills = db.Column(db.String(300))
    experience = db.Column(db.Text)
    resume_path = db.Column(db.String(200))

    is_blacklisted = db.Column(db.Boolean, default=False)

    applications = db.relationship(
        "Application", backref="student", cascade="all, delete-orphan"
    )
    placements = db.relationship(
        "Placement", backref="student", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Student {self.full_name}>"