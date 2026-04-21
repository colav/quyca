from typing import Tuple

from flask import Blueprint, jsonify, Response
from sentry_sdk import capture_exception

from quyca.domain.services import patent_service

patent_app_router = Blueprint("patent_app_router", __name__)

"""
@api {get} /app/patent/:patent_id Get patent by id
@apiName GetPatentById
@apiGroup Patent
@apiVersion 1.0.0
@apiDescription Obtiene una patente por ID.

@apiParam {String} patent_id ID de la patente.
"""


@patent_app_router.route("/<patent_id>", methods=["GET"])
def get_patent_by_id(patent_id: str) -> Response | Tuple[Response, int]:
    try:
        data = patent_service.get_patent_by_id(patent_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /app/patent/:patent_id/authors Get patent authors
@apiName GetPatentAuthors
@apiGroup Patent
@apiVersion 1.0.0
@apiDescription Obtiene los autores de una patente.

@apiParam {String} patent_id ID del patente.
"""


@patent_app_router.route("/<patent_id>/authors", methods=["GET"])
def get_patent_authors(patent_id: str) -> Response | Tuple[Response, int]:
    try:
        data = patent_service.get_patent_authors(patent_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
