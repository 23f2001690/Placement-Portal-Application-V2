"""
Creates the one and only admin account for the portal.
Run this once, right after the tables exist: python -m backend.seed_admin
There is no admin registration route on purpose - this script is the only
way an admin ever gets created.
"""
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User

ADMIN_EMAIL = "admin@placementportal.com"
ADMIN_PASSWORD = "Admin@457"


def seed_admin():
    app = create_app()
    with app.app_context():
        if User.query.filter_by(role="admin").first():
            print("Admin already exists, nothing to do.")
            return

        admin = User(email=ADMIN_EMAIL, role="admin")
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin created -> email: {ADMIN_EMAIL}, password: {ADMIN_PASSWORD}")


if __name__ == "__main__":
    seed_admin()