from typing import Any
from flask import Blueprint, jsonify
from sentry_sdk import capture_exception
from quyca.infrastructure.container import build_get_me_usecase

me_router = Blueprint("me_app_router", __name__)


@me_router.route("/me", methods=["GET"])
def me() -> tuple[Any, int]:
    try:
        usecase = build_get_me_usecase()
        result = usecase.execute()

        status_code = 200 if result.status == "sesion_activa" else 401

        payload: dict[str, Any] = {"status": result.status, "msg": result.msg}
        if result.user is not None:
            payload["user"] = result.user

        return jsonify(payload), status_code
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500
