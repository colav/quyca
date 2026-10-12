from typing import Tuple

from flask import Blueprint, request, jsonify, Response
from sentry_sdk import capture_exception

from quyca.domain.models.base_model import QueryParams
from quyca.domain.services import news_service
from quyca.domain.services.person import person_api_expert_service

person_api_router = Blueprint("person_api_router", __name__)


"""
@api {get} /person/:person_id/research/products Get works by person
@apiName GetWorksByPerson
@apiGroup API Expert
@apiVersion 1.0.0
@apiDescription Obtiene los productos bibliográficos asociados a un autor específico.

@apiParam {String} person_id ID del autor.
"""


@person_api_router.route("/<person_id>/research/products", methods=["GET"])
def get_works_by_person_api_expert(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = person_api_expert_service.get_works_by_person(person_id, query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /person/:person_id/research/news Get news by person
@apiName GetNewsByPerson
@apiGroup API Expert
@apiVersion 1.0.0
@apiDescription Obtiene las noticias asociadas a un autor específico.
@apiParam {String} person_id ID del autor.
"""


@person_api_router.route("/<person_id>/research/news")
def news_for_person(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = news_service.get_news_by_person(person_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /api/person/:person_id Get person by id
@apiName GetPersonById
@apiGroup API Expert
@apiVersion 1.0.0
@apiDescription Obtiene un autor por su ID.

@apiParam {String} person_id ID del autor.
"""


@person_api_router.route("/<person_id>", methods=["GET"])
def get_person_by_id(person_id: str) -> Response | Tuple[Response, int]:
    try:
        data = person_api_expert_service.get_person_by_id(person_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
