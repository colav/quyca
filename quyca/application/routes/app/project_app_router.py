from typing import Tuple

from flask import Blueprint, jsonify, Response
from sentry_sdk import capture_exception

from quyca.domain.services import project_service

project_app_router = Blueprint("project_app_router", __name__)

"""
@api {get} /app/project/:project_id Get project by id
@apiName GetProjectById
@apiGroup Project
@apiVersion 1.0.0
@apiDescription Obtiene un proyecto por ID.

@apiParam {String} project_id ID del proyecto.
"""


@project_app_router.route("/<project_id>", methods=["GET"])
def get_project_by_id(project_id: str) -> Response | Tuple[Response, int]:
    try:
        data = project_service.get_project_by_id(project_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /app/project/:project_id/authors Get project authors
@apiName GetProjectAuthors
@apiGroup Project
@apiVersion 1.0.0
@apiDescription Obtiene los autores de un proyecto.

@apiParam {String} project_id ID del proyecto.
"""


@project_app_router.route("/<project_id>/authors", methods=["GET"])
def get_project_authors(project_id: str) -> Response | Tuple[Response, int]:
    try:
        data = project_service.get_project_authors(project_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
