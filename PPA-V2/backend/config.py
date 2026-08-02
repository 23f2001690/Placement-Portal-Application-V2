import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "placement_portal.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "VENKI457"

    JWT_SECRET_KEY = "dev-jwt-secret-change-in-production"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    REDIS_URL = "redis://localhost:6379/0"
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # if unset, emails print to the console instead of sending for real - useful for demos
    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    SMTP_FROM = os.environ.get("SMTP_FROM", "placementcell@institute.edu")

    EXPORT_FOLDER = os.path.join(BASE_DIR, "exports")