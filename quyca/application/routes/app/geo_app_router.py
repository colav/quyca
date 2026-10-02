from typing import Tuple

from flask import Blueprint, json, jsonify, request
from sentry_sdk import capture_exception
from werkzeug.wrappers.response import Response

from quyca.domain.models.base_model import QueryParams
from quyca.domain.services.geo import geo_service
from quyca.domain.services.work import work_service


geo_app_router = Blueprint("geo_app_router", __name__)

""" 
"""


@geo_app_router.route("/<geo_type>/<geo_id>", methods=["GET"])
def get_geo_by_id(geo_type: str, geo_id: str) -> Response | Tuple[Response, int]:
    try:
        data = geo_service.geo_by_id(geo_type, geo_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
"""


@geo_app_router.route("/<geo_type>/<geo_id>/affiliations", methods=["GET"])
def get_affiliation_affiliations(geo_type: str, geo_id: str) -> Response | Tuple[Response, int]:
    try:
        data = geo_service.related_affiliations_by_geo(geo_type, geo_id)
        response_data = json.dumps(data, sort_keys=False)
        return Response(response_data, mimetype="application/json")
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
"""


@geo_app_router.route("/<geo_type>/<geo_id>/research/products", methods=["GET"])
def get_geo_products(geo_type: str, geo_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = work_service.get_works_by_geo(geo_type, geo_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
