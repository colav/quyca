from typing import Tuple

from flask import Blueprint, jsonify, Response
from sentry_sdk import capture_exception

from quyca.domain.services import work_service

work_app_router = Blueprint("work_app_router", __name__)

"""
@api {get} /app/works/:work_id Get work by id
@apiName GetWorkById
@apiGroup Work
@apiVersion 1.0.0
@apiDescription Obtiene un producto bibliográfico por ID.

@apiParam {String} work_id ID del producto bibliográfico.
"""


@work_app_router.route("/<work_id>", methods=["GET"])
def get_work_by_id(work_id: str) -> Response | Tuple[Response, int]:
    data = work_service.get_work_by_id(work_id)
    return jsonify(data)


"""
@api {get} /app/works/:work_id/authors Get work authors
@apiName GetWorkAuthors
@apiGroup Work
@apiVersion 1.0.0
@apiDescription Obtiene los autores de un producto bibliográfico.

@apiParam {String} work_id ID del producto bibliográfico.
"""


@work_app_router.route("/<work_id>/authors", methods=["GET"])
def get_work_authors(work_id: str) -> Response | Tuple[Response, int]:
    try:
        data = work_service.get_work_authors(work_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
