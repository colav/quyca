from typing import Tuple

from flask import Blueprint, jsonify, Response
from sentry_sdk import capture_exception

from quyca.services import project_service

project_router = Blueprint("project_app_router", __name__)


@project_router.route("/<project_id>", methods=["GET"])
def get_project_by_id(project_id: str) -> Response | Tuple[Response, int]:
    try:
        data = project_service.get_project_by_id(project_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@project_router.route("/<project_id>/authors", methods=["GET"])
def get_project_authors(project_id: str) -> Response | Tuple[Response, int]:
    try:
        data = project_service.get_project_authors(project_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
