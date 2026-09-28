from typing import Tuple
from flask import Blueprint, Response, jsonify, request
from sentry_sdk import capture_exception

from quyca.domain.models.base_model import QueryParams
from quyca.domain.services import work_service
from quyca.domain.services.export import export_service
from quyca.domain.services.source import source_plot_service, source_service


source_app_router = Blueprint("source_app_router", __name__)

"""
@api {get} /source/:source_id Get Source by ID
@apiName GetSourceById
@apiGroup Source
@apiVersion 1.0.0
@apiDescription Obtiene los detalles de una fuente específica utilizando su identificador único.

@apiParam {String} source_id Identificador único de la fuente.

@apiError (404) SourceNotFound The source with the specified ID was not found.

@apiErrorExample {json} Respuesta de error:
HTTP/1.1 404 Not Found
{
  "error": "Source not found"
}
"""


@source_app_router.route("/<source_id>", methods=["GET"])
def get_source_by_id(source_id: str) -> Response | Tuple[Response, int]:
    try:
        data = source_service.get_source_by_id(source_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 404


"""
@api {get} /app/source/:source_id/products Get works by source
@apiName GetSourceProducts
@apiGroup Source
@apiVersion 1.0.0
@apiDescription Obtiene los productos bibliográficos de una fuente.

@apiParam {String} source_id ID de la fuente.

@apiQuery {Number} [page=1] Número de la página.
@apiQuery {Number} [max=10] Número máximo de resultados.
@apiQuery {String} [sort] Campo a ordenar (citations, products, alphabetical). dirección del ordenamiento (asc/desc).
"""


@source_app_router.route("/<source_id>/products", methods=["GET"])
def get_source_products(source_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        if query_params.plot:
            data = source_plot_service.get_source_products_plot(source_id, query_params)
            return jsonify(data)
        data = work_service.get_works_by_source(source_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /app/source/:source_id/products/filters Get works filters by source
@apiName GetSourceProductsFilters
@apiGroup Source
@apiVersion 1.0.0
@apiDescription Obtiene los filtros disponibles en los productos bibliográficos de una fuente.

@apiParam {String} source_id ID de la fuente.

@apiQuery {Number} [page=1] Número de la página.
@apiQuery {Number} [max=10] Número máximo de resultados.
@apiQuery {String} [sort] Campo a ordenar (citations, products, alphabetical). dirección del ordenamiento (asc/desc).
"""


@source_app_router.route("/<source_id>/products/filters", methods=["GET"])
def get_source_products_filters(source_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = work_service.get_works_filters_by_source(source_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /app/source/:source_id/products/csv Get works csv by Source
@apiName GetSourceProductsCSV
@apiGroup Source
@apiVersion 1.0.0
@apiDescription Obtiene los productos bibliográficos de una fuente en formato CSV.

@apiParam {String} source_id ID de la afiliación.

@apiSuccessExample {csv} Success-Response:
HTTP/1.1 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename=source.csv
"""


@source_app_router.route("/<source_id>/products/csv", methods=["GET"])
def get_works_csv_by_source(source_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = export_service.get_works_csv_by_source(source_id, query_params)
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=source_works.csv"
        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /app/source/:source_id/products/excel Get works excel by Source
@apiName GetSourceProductsExcel
@apiGroup Source
@apiVersion 1.0.0
@apiDescription Obtiene los productos bibliográficos de una fuente en formato Excel.

@apiParam {String} source_id ID de la fuente.

@apiSuccessExample {excel} Success-Response:
HTTP/1.1 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename=source_works.xlsx
"""


@source_app_router.route("/<source_id>/products/excel", methods=["GET"])
def get_works_excel_by_source(source_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
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
