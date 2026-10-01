from typing import Tuple
from flask import Blueprint, request, jsonify, Response

from quyca.domain.models.base_model import QueryParams
from quyca.domain.services.source import source_api_expert_service

source_api_router = Blueprint("source_api_router", __name__)


"""
@api {get} /source/:source_id/research/products Get Research Products by Source
@apiName GetResearchProducts
@apiGroup Source
@apiVersion 1.0.0
@apiDescription Obtiene una lista paginada de productos de investigación publicados en una fuente específica.

@apiParam {String} source_id Identificador único de la fuente.

@apiQuery {Number} [page=1] Número de página para la paginación.
@apiQuery {Number} [max=10] Número máximo de resultados por página.
@apiQuery {String} [sort] Campo de ordenación.

@apiError (404) SourceNotFound The source with the specified ID was not found.

@apiErrorExample {json} Respuesta de error:
HTTP/1.1 404 Not Found
{
  "error": "Failed to retrieve research products"
}
"""


@source_api_router.route("/<source_id>/products", methods=["GET"])
def get_research_products(source_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = source_api_expert_service.get_works_by_source(source_id, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 404
