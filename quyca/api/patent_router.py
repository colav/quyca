from typing import Tuple

from flask import Blueprint, jsonify, Response
from sentry_sdk import capture_exception

from quyca.services import patent_service

patent_router = Blueprint("patent_app_router", __name__)


@patent_router.route("/<patent_id>", methods=["GET"])
def get_patent_by_id(patent_id: str) -> Response | Tuple[Response, int]:
    try:
        data = patent_service.get_patent_by_id(patent_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@patent_router.route("/<patent_id>/authors", methods=["GET"])
def get_patent_authors(patent_id: str) -> Response | Tuple[Response, int]:
    try:
        data = patent_service.get_patent_authors(patent_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
