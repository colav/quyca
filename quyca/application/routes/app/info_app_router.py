from typing import Tuple

from flask import Blueprint, jsonify, Response
from sentry_sdk import capture_exception

from quyca.domain.services import (
    info_service,
)

info_app_router = Blueprint("info_app_router", __name__)


@info_app_router.route("/info", methods=["GET"])
def get_info() -> Response | Tuple[Response, int]:
    try:
        data = info_service.get_info()
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@info_app_router.route("/info/quality", methods=["GET"])
def get_info_quality() -> Response | Tuple[Response, int]:
    try:
        data = info_service.get_works_quality_metrics()
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
