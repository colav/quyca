from typing import Tuple

from flask import Blueprint, request, jsonify, Response

from database.models.base_model import QueryParams
from services import (
    person_service,
    work_service,
    affiliation_service,
)

search_app_router = Blueprint("search_app_router", __name__)


@search_app_router.route("/person", methods=["GET"])
def search_persons() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = person_service.search_persons(query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@search_app_router.route("/works", methods=["GET"])
def search_works() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = work_service.search_works(query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@search_app_router.route("/affiliations/<affiliation_type>", methods=["GET"])
def search_affiliations(affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = affiliation_service.search_affiliations(affiliation_type, query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
