from flask import Blueprint, request, Response, jsonify

from database.models.base_model import QueryParams
from services import new_affiliation_service, new_work_service

affiliation_app_router = Blueprint("affiliation_app_router", __name__)


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>", methods=["GET"])
def get_affiliation_by_id(affiliation_type: str, affiliation_id: str):
    try:
        data = new_affiliation_service.get_affiliation_by_id(affiliation_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/affiliations", methods=["GET"])
def get_affiliation_affiliations(affiliation_type: str, affiliation_id: str):
    try:
        data = new_affiliation_service.get_related_affiliations_by_affiliation(
            affiliation_id, affiliation_type
        )
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@affiliation_app_router.route(
    "/<affiliation_type>/<affiliation_id>/research/products", methods=["GET"]
)
def get_affiliation_research_products(affiliation_id: str, affiliation_type: str):
    try:
        query_params = QueryParams(**request.args)
        if query_params.plot:
            data = new_affiliation_service.get_affiliation_plot(
                affiliation_id, affiliation_type, query_params
            )
            return jsonify(data)
        data = new_work_service.get_works_by_affiliation(
            affiliation_id, affiliation_type, query_params
        )
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@affiliation_app_router.route(
    "/<affiliation_type>/<affiliation_id>/research/products/csv", methods=["GET"]
)
def get_works_csv_by_affiliation(affiliation_type: str, affiliation_id: str):
    try:
        data = new_work_service.get_works_csv_by_affiliation(affiliation_id, affiliation_type)
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=affiliation.csv"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 400
