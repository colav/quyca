import json
from typing import Tuple

from flask import Blueprint, request, Response, jsonify, stream_with_context
from sentry_sdk import capture_exception

from quyca.domain.models.base_model import QueryParams
from quyca.domain.services import (
    news_service,
)
from quyca.domain.services.affiliation import affiliation_plot_service, affiliation_service
from quyca.domain.services.export import export_affiliation_plot_service, export_service
from quyca.domain.services.patent import patent_service
from quyca.domain.services.project import project_service
from quyca.domain.services.work import work_service

affiliation_router = Blueprint("affiliation_app_router", __name__)


@affiliation_router.route("/<affiliation_type>/<affiliation_id>", methods=["GET"])
def get_affiliation_by_id(affiliation_type: str, affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        data = affiliation_service.get_affiliation_by_id(affiliation_id, affiliation_type)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_router.route("/<affiliation_type>/<affiliation_id>/affiliations", methods=["GET"])
def get_affiliation_affiliations(affiliation_type: str, affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        data = affiliation_service.get_related_affiliations_by_affiliation(affiliation_id, affiliation_type)
        response_data = json.dumps(data, sort_keys=False)
        return Response(response_data, mimetype="application/json")
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_router.route("/<affiliation_type>/<affiliation_id>/research/products", methods=["GET"])
def get_affiliation_research_products(affiliation_type: str, affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        if query_params.plot:
            data = affiliation_plot_service.get_affiliation_plot(affiliation_id, affiliation_type, query_params)
            return jsonify(data)
        data = work_service.get_works_by_affiliation(affiliation_id, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_router.route("/<affiliation_type>/<affiliation_id>/research/products/filters", methods=["GET"])
def get_affiliation_research_products_filters(
    affiliation_type: str, affiliation_id: str
) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = work_service.get_works_filters_by_affiliation(affiliation_id, affiliation_type, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_router.route("/<affiliation_type>/<affiliation_id>/research/products/csv", methods=["GET"])
def get_works_csv_by_affiliation(affiliation_type: str, affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        if query_params.plot:
            data = export_affiliation_plot_service.get_plot_csv(affiliation_id, affiliation_type, query_params)
            response = Response(data, content_type="text/csv; charset=utf-8")
            response.headers["Content-Disposition"] = f'attachment; filename="{query_params.plot}.csv"'
            return response
        data = export_service.get_works_csv_by_affiliation(affiliation_id, affiliation_type, query_params)
        response = Response(stream_with_context(data), content_type="text/csv; charset=utf-8")
        response.headers["Content-Disposition"] = "attachment; filename=affiliations.csv"
        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_router.route(
    "/<affiliation_type>/<affiliation_id>/research/products/excel",
    methods=["GET"],
)
def get_works_excel_by_affiliation(affiliation_type: str, affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = export_service.get_works_excel_by_affiliation(
            affiliation_id,
            affiliation_type,
            query_params,
        )
        response = Response(
            data.getvalue(),
            content_type=("application/vnd.openxmlformats-officedocument." "spreadsheetml.sheet"),
        )
        response.headers["Content-Disposition"] = "attachment; filename=affiliations.xlsx"
        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_router.route("/<affiliation_type>/<affiliation_id>/research/patents", methods=["GET"])
def get_affiliation_research_patents(affiliation_id: str, affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = patent_service.get_patents_by_affiliation(affiliation_id, affiliation_type, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_router.route("/<affiliation_type>/<affiliation_id>/research/projects", methods=["GET"])
def get_affiliation_research_projects(affiliation_id: str, affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = project_service.get_projects_by_affiliation(affiliation_id, affiliation_type, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@affiliation_router.route("/<affiliation_type>/<affiliation_id>/research/news")
def get_affiliation_research_news(affiliation_id: str, affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = news_service.get_news_by_affiliation(affiliation_id, affiliation_type, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
