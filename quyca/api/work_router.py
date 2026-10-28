from typing import Tuple

from flask import Blueprint, jsonify, Response, request
from sentry_sdk import capture_exception

from quyca.models.base_model import QueryParams
from quyca.services import work_service

work_router = Blueprint("work_app_router", __name__)


@work_router.route("/<work_id>", methods=["GET"])
def get_work_by_id(work_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = work_service.get_work_by_id(work_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@work_router.route("", methods=["GET"])
def get_work_by_doi() -> Response | Tuple[Response, int]:
    doi = request.args.get("doi")
    if not doi:
        return jsonify({"error": "Missing required parameter: doi"}), 401
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = work_service.get_work_by_doi(doi, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@work_router.route("/<work_id>/authors", methods=["GET"])
def get_work_authors(work_id: str) -> Response | Tuple[Response, int]:
    try:
        data = work_service.get_work_authors(work_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
