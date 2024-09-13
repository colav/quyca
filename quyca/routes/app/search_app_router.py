from flask import Blueprint, request, jsonify

from database.models.base_model import QueryParams
from services import (
    new_person_service,
    new_work_service,
    new_affiliation_service,
)

search_app_router = Blueprint("search_app_router", __name__)


@search_app_router.route("/person", methods=["GET"])
def search_persons():
    try:
        query_params = QueryParams(**request.args)
        data = new_person_service.search_persons(query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@search_app_router.route("/works", methods=["GET"])
def search_works():
    try:
        query_params = QueryParams(**request.args)
        data = new_work_service.search_works(query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@search_app_router.route("/affiliations/<affiliation_type>", methods=["GET"])
def search_affiliations(affiliation_type: str):
    try:
        query_params = QueryParams(**request.args)
        data = new_affiliation_service.search_affiliations(affiliation_type, query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
