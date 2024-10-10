from typing import Tuple

from flask import Blueprint, request, jsonify, Response
from sentry_sdk import capture_exception

from domain.models.base_model import QueryParams
from domain.services import (
    work_service,
    person_service,
    affiliation_service,
    other_work_service,
    project_service,
    patent_service,
)

search_app_router = Blueprint("search_app_router", __name__)


@search_app_router.route("/person", methods=["GET"])
def search_persons() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = person_service.search_persons(query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_app_router.route("/works", methods=["GET"])
def search_works() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = work_service.search_works(query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_app_router.route("/works/filters", methods=["GET"])
def get_search_works_filters() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = work_service.get_search_works_available_filters(query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_app_router.route("/affiliations/<affiliation_type>", methods=["GET"])
def search_affiliations(affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = affiliation_service.search_affiliations(affiliation_type, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_app_router.route("/other_works", methods=["GET"])
def search_other_works() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = other_work_service.search_other_works(query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_app_router.route("/patents", methods=["GET"])
def search_patents() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = patent_service.search_patents(query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_app_router.route("/projects", methods=["GET"])
def search_projects() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = project_service.search_projects(query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
