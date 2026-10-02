from typing import Tuple
from flask import Blueprint, request, jsonify, Response

from quyca.domain.models.base_model import QueryParams
from quyca.domain.services.geo import geo_api_expert_service

geo_api_router = Blueprint("geo_api_router", __name__)

"""
Get research products by geo type and geo id.
"""


@geo_api_router.route("/<geo_type>/<geo_id>/research/products", methods=["GET"])
def get_research_products(geo_type: str, geo_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = geo_api_expert_service.get_works_by_geo(geo_type, geo_id, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 404
