import os
from flask import Flask, render_template, send_from_directory

from backend.config import Config
from backend.extensions import db, jwt

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
SRC_DIR = os.path.join(FRONTEND_DIR, "src")


def create_app():
    app = Flask(__name__, template_folder=FRONTEND_DIR)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        import backend.models  # noqa: F401
        db.create_all()

    from backend.routes.auth import auth_bp
    from backend.routes.admin import admin_bp
    from backend.routes.company import company_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/src/<path:filename>")
    def serve_frontend_src(filename):
        response = send_from_directory(SRC_DIR, filename)
        if filename.endswith(".vue") or filename.endswith(".js"):
            response.headers["Content-Type"] = "application/javascript"
        return response

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)