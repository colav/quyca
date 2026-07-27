import os

import sentry_sdk
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_compress import Compress
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration

from quyca.application.routes.router import router, limiter
from quyca.config import Settings


def create_app() -> Flask:
    app_settings = Settings()  # type: ignore[call-arg]
    sentry_sdk.init(
        dsn=app_settings.SENTRY_DSN,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

    project_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(project_dir, "application", "static")
    app_factory = Flask(__name__, static_folder=static_dir)

    app_factory.config["JWT_SECRET_KEY"] = app_settings.JWT_SECRET_KEY
    app_factory.config["JWT_ACCESS_TOKEN_EXPIRES"] = app_settings.JWT_ACCESS_TOKEN_EXPIRES
    app_factory.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app_factory.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"
    app_factory.config["JWT_COOKIE_HTTPONLY"] = True
    app_factory.config["JWT_COOKIE_SAMESITE"] = "None"
    app_factory.config["JWT_COOKIE_SECURE"] = True
    app_factory.config["JWT_COOKIE_CSRF_PROTECT"] = True
    app_factory.config["JWT_CSRF_IN_COOKIES"] = True
    app_factory.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    app_factory.config["JWT_COOKIE_DOMAIN"] = ".impactu.colav.co"
    app_factory.config["LOCAL_STORAGE_PATH"] = app_settings.LOCAL_STORAGE_PATH
    app_factory.config["GOOGLE_CREDENTIALS"] = app_settings.GOOGLE_CREDENTIALS
    app_factory.config["GOOGLE_PARENT_ID"] = app_settings.GOOGLE_PARENT_ID

    JWTManager(app_factory)

    CORS(
        app_factory,
        supports_credentials=True,
        origins=["http://localhost:3000", r"https?://(.*\.)?impactu\.colav\.co$"],
    )
    app_factory.register_blueprint(router)
    Compress(app_factory)
    return app_factory


if __name__ == "__main__":
    settings = Settings()  # type: ignore[call-arg]
    app = create_app()
    limiter.init_app(app)
    app.run(host="0.0.0.0", port=int(settings.APP_PORT), debug=settings.APP_DEBUG, threaded=True)
