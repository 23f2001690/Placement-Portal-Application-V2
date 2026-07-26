from flask import Flask

from backend.config import Config
from backend.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        import backend.models  # noqa: F401  (registers all tables with SQLAlchemy)
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)