from flask import Blueprint

from core.config import settings

ping_router = Blueprint("ping_router", __name__)


@ping_router.route("/ping", methods=["GET"])
def read_root():
    """Ping the API."""
    result = {"ping": str(settings.MONGO_URI)}
    return result
