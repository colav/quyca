from typing import Tuple

from flask import Blueprint, request, jsonify
from werkzeug.wrappers.response import Response
from sentry_sdk import capture_exception

from quyca.models.base_model import QueryParams
from quyca.services import search_service

search_router = Blueprint("search_router", __name__)


@search_router.route("/person", methods=["GET"])
def search_persons() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_persons(query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_router.route("/works", methods=["GET"])
def search_works() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_works(query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_router.route("/affiliations/<affiliation_type>", methods=["GET"])
def search_affiliations(affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_affiliations(query_params, affiliation_type, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_router.route("/sources", methods=["GET"])
def search_sources() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_sources(query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_router.route("/patents", methods=["GET"])
def search_patents() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_patents(query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_router.route("/projects", methods=["GET"])
def search_projects() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_projects(query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_router.route("/geo/<geo_type>", methods=["GET"])
def search_geo(geo_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        if geo_type not in {"city", "state"}:
            return jsonify({"error": "Invalid geo_type. Allowed values: city, state"}), 400
        data = search_service.search_geo(query_params, geo_type, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_router.route("/works/filters", methods=["GET"])
def get_search_works_filters() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_works_available_filters(query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_router.route("/affiliations/<affiliation_type>/filters", methods=["GET"])
def get_search_affiliations_filters(affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_affiliations_available_filters(affiliation_type, query_params)
        return jsonify(data), 200
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_router.route("/sources/filters", methods=["GET"])
def get_search_sources_filters() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_sources_available_filters(query_params)
        return jsonify(data), 200
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
