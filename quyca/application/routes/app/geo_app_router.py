from typing import Tuple

from flask import Blueprint, json, jsonify, request
from sentry_sdk import capture_exception
from werkzeug.wrappers.response import Response

from quyca.domain.models.base_model import QueryParams
from quyca.domain.services.geo import geo_service
from quyca.domain.services.work import work_service


geo_app_router = Blueprint("geo_app_router", __name__)

"""
@api {get} /app/geo/:geo_type/:geo_id Get geographic entity by id
@apiName GetGeoById
@apiGroup Geo

@apiVersion 1.0.0

@apiDescription Obtiene una entidad geográfica específica por su tipo e ID. El tipo de entidad puede ser una ciudad (city) o un departamento/estado (state).

@apiParam {String} geo_type Tipo de entidad geográfica. Valores permitidos: "city" o "state".
@apiParam {String} geo_id ID de la entidad geográfica. Para ciudades corresponde al código DANE de la ciudad y para estados/departamentos al código DANE del departamento.

@apiSuccess {Object} data Información de la entidad geográfica.

@apiError {Object} 400 Error al obtener la entidad geográfica.

@apiErrorExample {json} 400
{
  "error": "The state with id 001 does not exist."
}
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
@api {get} /app/geo/:geo_type/:geo_id/affiliations Get affiliations by geographic entity
@apiName GetAffiliationAffiliations
@apiGroup Geo
@apiVersion 1.0.0
@apiDescription Obtiene las afiliaciones relacionadas con una entidad geográfica específica. Para una entidad de tipo "state" retorna instituciones, grupos y ciudades relacionadas. Para una entidad de tipo "city" retorna únicamente instituciones y grupos relacionados.

@apiParam {String} geo_type Tipo de entidad geográfica. Valores permitidos: "city" o "state".
@apiParam {String} geo_id ID de la entidad geográfica. Para ciudades corresponde al código DANE de la ciudad y para estados/departamentos al código DANE del departamento.

@apiSuccess {Object} institutions Instituciones relacionadas con la entidad geográfica. Disponible para "state" y "city".
@apiSuccess {Object} groups Grupos relacionados con la entidad geográfica. Disponible para "state" y "city".
@apiSuccess {Object} cities Ciudades relacionadas con la entidad geográfica. Disponible únicamente cuando geo_type es "state".

@apiSuccessExample {json} State
{
  "institutions": [],
  "groups": [],
  "cities": []
}

@apiSuccessExample {json} City
{
  "institutions": [],
  "groups": []
}

@apiError {Object} 400 Error al obtener las afiliaciones relacionadas con la entidad geográfica.

@apiErrorExample {json} 400
{
  "error": "Error message"
}
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
@api {get} /app/geo/:geo_type/:geo_id/research/products Get research products by geographic entity
@apiName GetGeoProducts
@apiGroup Geo
@apiVersion 1.0.0

@apiDescription Obtiene los productos bibliográficos asociados a una entidad geográfica específica. La entidad puede ser una ciudad o un departamento/estado. Los resultados pueden ser filtrados y paginados mediante los parámetros de consulta disponibles en QueryParams.
@apiParam {String} geo_type Tipo de entidad geográfica. Valores permitidos: "city" o "state".
@apiParam {String} geo_id ID de la entidad geográfica. Para ciudades corresponde al código DANE de la ciudad y para estados/departamentos al código DANE del departamento.

@apiQuery {String} [page] Número de página de los resultados.
@apiQuery {String} [limit] Cantidad máxima de productos bibliográficos por página.
@apiQuery {String} [sort] Campo por el cual ordenar los resultados. Puede ser "citaciones", "alfabetico".

@apiSuccess {Array} data Lista de productos bibliográficos asociados a la entidad geográfica.

@apiSuccessExample {json}
{
  "data": [
    {}
  ]
}

@apiError {Object} 400 Error al obtener los productos bibliográficos asociados a la entidad geográfica.

@apiErrorExample {json} 400
{
  "error": "Error message"
}
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
