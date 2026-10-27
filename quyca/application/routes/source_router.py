from typing import Tuple
from flask import Blueprint, Response, jsonify, request
from sentry_sdk import capture_exception

from quyca.domain.models.base_model import QueryParams
from quyca.domain.services.work import work_service
from quyca.domain.services.export import export_service
from quyca.domain.services.source import source_plot_service, source_service


source_router = Blueprint("source_app_router", __name__)


@source_router.route("/<source_id>", methods=["GET"])
def get_source_by_id(source_id: str) -> Response | Tuple[Response, int]:
    try:
        data = source_service.get_source_by_id(source_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 404


@source_router.route("/<source_id>/products", methods=["GET"])
def get_source_products(source_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        if query_params.plot:
            data = source_plot_service.get_source_products_plot(source_id, query_params)
            return jsonify(data)
        data = work_service.get_works_by_source(source_id, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@source_router.route("/<source_id>/products/filters", methods=["GET"])
def get_source_products_filters(source_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = work_service.get_works_filters_by_source(source_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@source_router.route("/<source_id>/products/csv", methods=["GET"])
def get_works_csv_by_source(source_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = export_service.get_works_csv_by_source(source_id, query_params)
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=source_works.csv"
        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@source_router.route("/<source_id>/products/excel", methods=["GET"])
def get_works_excel_by_source(source_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = export_service.get_works_excel_by_source(source_id, query_params)
        response = Response(
            data.getvalue(),
            content_type=("application/vnd.openxmlformats-officedocument." "spreadsheetml.sheet"),
        )
        response.headers["Content-Disposition"] = "attachment; filename=source_works.xlsx"
        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
