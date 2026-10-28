from typing import Any
from flask import Blueprint, jsonify
from sentry_sdk import capture_exception
from quyca.services import auth_service

me_router = Blueprint("me_app_router", __name__)


@me_router.route("/me", methods=["GET"])
def get_session() -> tuple[Any, int]:
    try:
        payload = auth_service.get_session()
        status_code = 200 if payload["status"] == auth_service.SESION_ACTIVA else 401
        return jsonify(payload), status_code
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500
