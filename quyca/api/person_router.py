from typing import Tuple

from flask import Blueprint, request, Response, jsonify, stream_with_context
from sentry_sdk import capture_exception

from quyca.models.base_model import QueryParams
from quyca.services import news_service
from quyca.services import export_service
from quyca.services import patent_service
from quyca.services import person_plot_service, person_service
from quyca.services import project_service
from quyca.services import work_service

person_router = Blueprint("person_app_router", __name__)


@person_router.route("/<person_id>", methods=["GET"])
def get_person_by_id(person_id: str) -> Response | Tuple[Response, int]:
    try:
        data = person_service.get_person_by_id(person_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@person_router.route("/<person_id>/research/products", methods=["GET"])
def get_person_research_products(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        if query_params.plot:
            data = person_plot_service.get_person_plot(person_id, query_params)
            return jsonify(data)
        data = work_service.get_works_by_person(person_id, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@person_router.route("/<person_id>/research/products/filters", methods=["GET"])
def get_person_research_products_filters(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = work_service.get_works_filters_by_person(person_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@person_router.route("/<person_id>/research/products/csv", methods=["GET"])
def get_works_csv_by_person(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = export_service.get_works_csv_by_person(person_id, query_params)
        response = Response(stream_with_context(data), content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=person_works.csv"
        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@person_router.route("/<person_id>/research/products/excel", methods=["GET"])
def get_works_excel_by_person(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = export_service.get_works_excel_by_person(person_id, query_params)
        response = Response(
            data.getvalue(),
            content_type=("application/vnd.openxmlformats-officedocument." "spreadsheetml.sheet"),
        )
        response.headers["Content-Disposition"] = "attachment; filename=person_works.xlsx"
        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@person_router.route("/<person_id>/research/patents", methods=["GET"])
def get_person_research_patents(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = patent_service.get_patents_by_person(person_id, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@person_router.route("/<person_id>/research/projects", methods=["GET"])
def get_person_research_projects(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = project_service.get_projects_by_person(person_id, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@person_router.route("/<person_id>/research/news")
def get_person_research_news(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = news_service.get_news_by_person(person_id, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
