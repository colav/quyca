from typing import Tuple

from flask import Blueprint, request, Response, jsonify

from domain.models.base_model import QueryParams
from domain.services import (
    work_service,
    person_service,
    other_work_service,
    project_service,
    person_plot_service,
    csv_service,
    patent_service,
)

person_app_router = Blueprint("person_app_router", __name__)


@person_app_router.route("/<person_id>", methods=["GET"])
def get_person_by_id(person_id: str) -> Response | Tuple[Response, int]:
    try:
        data = person_service.get_person_by_id(person_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@person_app_router.route("/<person_id>/research/products", methods=["GET"])
def get_person_research_products(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        if query_params.plot:
            data = person_plot_service.get_person_plot(person_id, query_params)
            return jsonify(data)
        data = work_service.get_works_by_person(person_id, query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@person_app_router.route("/<person_id>/research/products/csv", methods=["GET"])
def get_works_csv_by_person(person_id: str) -> Response | Tuple[Response, int]:
    try:
        data = csv_service.get_works_csv_by_person(person_id)
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=affiliation.csv"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@person_app_router.route("/<person_id>/research/other_works", methods=["GET"])
def get_person_research_other_works(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = other_work_service.get_other_works_by_person(person_id, query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@person_app_router.route("/<person_id>/research/patents", methods=["GET"])
def get_person_research_patents(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = patent_service.get_patents_by_person(person_id, query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@person_app_router.route("/<person_id>/research/projects", methods=["GET"])
def get_person_research_projects(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = project_service.get_projects_by_person(person_id, query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
