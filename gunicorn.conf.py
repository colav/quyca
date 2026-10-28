# Loaded automatically by gunicorn from the working directory (/app in the containers).
from quyca.config import settings

wsgi_app = "quyca.app:create_app()"
bind = f"0.0.0.0:{settings.APP_PORT}"
workers = settings.GUNICORN_WORKERS
timeout = settings.GUNICORN_TIMEOUT
reload = settings.APP_DEBUG
accesslog = "-"
errorlog = "-"
