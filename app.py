import os
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from database import close_db, fetch_all, init_db
from seed import seed_if_empty
from qr_service import generate_qr_image, qr_filename, verification_url
from routes.public import public_bp
from routes.auth import auth_bp
from routes.admin import admin_bp


def ensure_qr_files(app):
    base = app.config.get("BASE_URL") or "http://127.0.0.1:5000"
    for row in fetch_all("SELECT unique_code FROM perfumes"):
        path = os.path.join(app.config["QR_FOLDER"], qr_filename(row["unique_code"]))
        generate_qr_image(verification_url(base, row["unique_code"]), path)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    if (app.config.get("BASE_URL") or "").startswith("https"):
        app.config["PREFERRED_URL_SCHEME"] = "https"
    os.makedirs(app.config["QR_FOLDER"], exist_ok=True)

    with app.app_context():
        init_db()
        seed_if_empty()
        ensure_qr_files(app)

    app.teardown_appcontext(close_db)
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
