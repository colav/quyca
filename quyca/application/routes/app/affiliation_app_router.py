import json
from typing import Tuple

from flask import Blueprint, request, Response, jsonify
from sentry_sdk import capture_exception

from domain.models.base_model import QueryParams
from domain.services import (
    work_service,
    affiliation_service,
    other_work_service,
    project_service,
    affiliation_plot_service,
    csv_service,
    patent_service,
)

affiliation_app_router = Blueprint("affiliation_app_router", __name__)


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>", methods=["GET"])
def get_affiliation_by_id(affiliation_type: str, affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        data = affiliation_service.get_affiliation_by_id(affiliation_id, affiliation_type)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/affiliations", methods=["GET"])
def get_affiliation_affiliations(affiliation_type: str, affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        data = affiliation_service.get_related_affiliations_by_affiliation(affiliation_id, affiliation_type)
        response_data = json.dumps(data, sort_keys=False)
        return Response(response_data, mimetype="application/json")
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/research/products", methods=["GET"])
def get_affiliation_research_products(affiliation_id: str, affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        if query_params.plot:
            data = affiliation_plot_service.get_affiliation_plot(affiliation_id, affiliation_type, query_params)
            return jsonify(data)
        data = work_service.get_works_by_affiliation(affiliation_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/research/products/filters", methods=["GET"])
def get_affiliation_research_products_filters(
    affiliation_id: str, affiliation_type: str
) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = work_service.get_works_filters_by_affiliation(affiliation_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/research/products/csv", methods=["GET"])
def get_works_csv_by_affiliation(affiliation_type: str, affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        data = csv_service.get_works_csv_by_affiliation(affiliation_id)
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=affiliation.csv"
        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/research/other_works", methods=["GET"])
def get_affiliation_research_other_works(affiliation_id: str, affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = other_work_service.get_other_works_by_affiliation(affiliation_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/research/patents", methods=["GET"])
def get_affiliation_research_patents(affiliation_id: str, affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = patent_service.get_patents_by_affiliation(affiliation_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/research/projects", methods=["GET"])
def get_affiliation_research_projects(affiliation_id: str, affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = project_service.get_projects_by_affiliation(affiliation_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
