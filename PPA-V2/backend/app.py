import os
import mimetypes
from flask import Flask, render_template

from backend.config import Config
from backend.extensions import db, jwt

mimetypes.add_type("application/javascript", ".vue")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")


def create_app():
    app = Flask(
        __name__,
        template_folder=FRONTEND_DIR,
        static_folder=os.path.join(FRONTEND_DIR, "src"),
        static_url_path="/src",
    )
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        import backend.models  # noqa: F401
        db.create_all()

    from backend.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)