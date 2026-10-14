from typing import Tuple

from flask import Blueprint, request, jsonify
from werkzeug.wrappers.response import Response
from sentry_sdk import capture_exception

from quyca.domain.models.base_model import QueryParams
from quyca.domain.services.search import search_service

search_router = Blueprint("search_router", __name__)


"""
@api {get} /person Buscar personas
@apiName SearchPersons
@apiGroup API Expert
@apiDescription Redirige la búsqueda de personas al router principal.

@apiParam (Query Params) {String} [keywords] Palabras clave de búsqueda (nombre o parte del nombre de la persona).
@apiParam (Query Params) {String} [countries] País de afiliación o nacionalidad.
@apiParam (Query Params) {String} [subjects] Área de conocimiento o disciplina.
@apiParam (Query Params) {Number{1..250}} [limit] Límite de resultados por página.
@apiParam (Query Params) {Number} [page] Página de resultados a obtener.
"""


@search_router.route("/person", methods=["GET"])
def search_persons() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_persons(query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /works Buscar productos
@apiName SearchWorks
@apiGroup API Expert
@apiDescription Busca productos en el sistema según los filtros y parámetros definidos.

@apiParam (Query Params) {Number{1..250}} [limit] Límite máximo de resultados (alias: `max`).
@apiParam (Query Params) {Number} [page] Número de página a consultar.
@apiParam (Query Params) {String} [keywords] Palabras clave para filtrar productos.
@apiParam (Query Params) {String} [sort] Criterio de ordenamiento (por ejemplo: `year:desc`).
@apiParam (Query Params) {String} [product_types] Tipos de producto asociados al producto.
@apiParam (Query Params) {String} [years] Años de publicación (rango o lista separada por comas).
@apiParam (Query Params) {String} [topics] Tópicos de investigación o categorías.
@apiParam (Query Params) {String} [countries] Países asociados al trabajo o sus autores.
@apiParam (Query Params) {String} [authors_ranking] Ranking de autores.

@apiError (400) {String} error Mensaje de error en caso de fallo o parámetros inválidos.
"""


@search_router.route("/works", methods=["GET"])
def search_works() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_works(query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /affiliations/:affiliation_type Buscar afiliaciones
@apiName SearchAffiliations
@apiGroup API Expert
@apiDescription Redirige la búsqueda de afiliaciones según el tipo especificado.

@apiParam (Path) {String} affiliation_type Tipo de afiliación (por ejemplo: `institution`, `faculty`, `department`, `group`).
@apiParam (Query Params) {String} [keywords] Palabras clave de búsqueda.
@apiParam (Query Params) {String} [countries] País o región de la afiliación.
@apiParam (Query Params) {String} [sort] Criterio de ordenamiento (por ejemplo: `name:asc`).
@apiParam (Query Params) {Number{1..250}} [limit] Límite de resultados por página.
@apiParam (Query Params) {Number} [page] Página actual de la búsqueda.
"""


@search_router.route("/affiliations/<affiliation_type>", methods=["GET"])
def search_affiliations(affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_affiliations(query_params, affiliation_type, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /sources Buscar fuentes
@apiName SearchSources
@apiGroup API Expert
@apiDescription Redirige la búsqueda de fuentes (journals, libros, conferencias, etc.) al router principal.

@apiParam (Query Params) {String} [source_types] Tipo de fuente (por ejemplo: `journal`, `book`, `conference`).
@apiParam (Query Params) {String} [keywords] Palabras clave de búsqueda.
@apiParam (Query Params) {String} [countries] País o región.
@apiParam (Query Params) {Number{1..250}} [limit] Límite máximo de resultados por página.
@apiParam (Query Params) {Number} [page] Página de resultados.
"""


@search_router.route("/sources", methods=["GET"])
def search_sources() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_sources(query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


""" 
@api {get} /patents Buscar patentes
@apiName SearchPatents
@apiGroup API Expert
@apiDescription Busca patentes en el sistema según los filtros y parámetros definidos.

@apiParam (Query Params) {Number{1..250}} [limit] Límite máximo de resultados (alias: `max`).
@apiParam (Query Params) {Number} [page] Número de página a consultar.
@apiParam (Query Params) {String} [keywords] Palabras clave para filtrar patentes.
@apiParam (Query Params) {String} [sort] Criterio de ordenamiento (por ejemplo: `year:desc`).
"""


@search_router.route("/patents", methods=["GET"])
def search_patents() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_patents(query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


""" 
@api {get} /projects Buscar proyectos
@apiName SearchProjects
@apiGroup API Expert
@apiDescription Busca proyectos en el sistema según los filtros y parámetros definidos.

@apiParam (Query Params) {Number{1..250}} [limit] Límite máximo de resultados (alias: `max`).
@apiParam (Query Params) {Number} [page] Número de página a consultar.
@apiParam (Query Params) {String} [keywords] Palabras clave para filtrar proyectos.
@apiParam (Query Params) {String} [sort] Criterio de ordenamiento (por ejemplo: `year:desc`).
"""


@search_router.route("/projects", methods=["GET"])
def search_projects() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_projects(query_params, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /geo/:geo_type Buscar entidades geográficas
@apiName SearchGeo
@apiGroup API Expert
@apiDescription Busca entidades geográficas de Colombia según el tipo especificado.

@apiParam (Path) {String} geo_type Tipo de entidad geográfica (por ejemplo: `states`, `city`).
@apiParam (Query Params) {String} [keywords] Palabras clave de búsqueda.
@apiParam (Query Params) {Number{1..250}} [limit] Límite máximo de resultados por página.
@apiParam (Query Params) {Number} [page] Número de página a consultar.
@apiParam (Query Params) {String} [sort] Criterio de ordenamiento (por ejemplo: `name:asc`).

@apiSuccess (Success 200) {Object[]} data Lista de entidades geográficas encontradas.
@apiError (400) {String} error Mensaje de error en caso de fallo o parámetros inválidos.
"""


@search_router.route("/geo/<geo_type>", methods=["GET"])
def search_geo(geo_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        if geo_type not in {"city", "state"}:
            return jsonify({"error": "Invalid geo_type. Allowed values: city, state"}), 400
        data = search_service.search_geo(query_params, geo_type, request.url)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /search/works/filters Search works filters
@apiName SearchWorksFilters
@apiGroup Search
@apiVersion 1.0.0

@apiDescription Obtiene los filtros disponibles para la búsqueda de productos bibliográficos. Los filtros retornados dependen de los criterios de búsqueda y filtros aplicados en la solicitud.

@apiParam {String} [product_types] Filtra por tipos de producto bibliográfico.
@apiParam {String} [years] Filtra por años de publicación.
@apiParam {String} [status] Filtra por estado del producto bibliográfico.
@apiParam {String} [subjects] Filtra por áreas o materias asociadas al producto.
@apiParam {String} [topics] Filtra por temas asociados al producto.
@apiParam {String} [countries] Filtra por países asociados al producto.
@apiParam {String} [groups_ranking] Filtra por rankings relacionados con grupos de investigación.
@apiParam {String} [authors_ranking] Filtra por rankings relacionados con autores.

@apiSuccess {Object} product_types Tipos de productos bibliográficos disponibles como filtro.
@apiSuccess {Object[]} years Años de publicación disponibles como filtro.
@apiSuccess {Object} status Estados disponibles para filtrar los productos.
@apiSuccess {Object} topics Temas disponibles como filtro.
@apiSuccess {Object} countries Países disponibles como filtro.
@apiSuccess {Object} groups_ranking Rankings disponibles relacionados con grupos de investigación.
@apiSuccess {Object} authors_ranking Rankings disponibles relacionados con autores.

@apiError {Object} 400 Error en los parámetros de búsqueda o durante el procesamiento de la solicitud.
@apiError {String} 400.error Descripción del error.
@apiErrorExample {json} BadRequest:
{ 
    "error": "Invalid query parameters" 
}
"""


@search_router.route("/works/filters", methods=["GET"])
def get_search_works_filters() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_works_available_filters(query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /search/affiliations/:affiliation_type/filters Get affiliation filters
@apiName GetSearchAffiliationsFilters
@apiGroup Search
@apiVersion 1.0.0

@apiDescription Get available state and city filters for affiliations by affiliation type.
@apiParam {String} affiliation_type Affiliation type (e.g. "institution", "faculty", "group", "department").

@apiSuccess {Object[]} states List of available state filters.
@apiSuccess {Number} states.count Number of affiliations associated with the state.
@apiSuccess {String} states.label Normalized state name displayed to the user.
@apiSuccess {String} states.value State value used by the filter.
@apiSuccess {Object[]} cities List of available city filters.
@apiSuccess {Number} cities.count Number of affiliations associated with the city.
@apiSuccess {String} cities.label Normalized city name displayed to the user.
@apiSuccess {String} cities.value City value used by the filter.
"""


@search_router.route("/affiliations/<affiliation_type>/filters", methods=["GET"])
def get_search_affiliations_filters(affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_affiliations_available_filters(affiliation_type, query_params)
        return jsonify(data), 200
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /search/sources/filters Search source filters
@apiName SearchWorksFilters
@apiGroup Search
@apiVersion 1.0.0

@apiDescription Obtiene los filtros disponibles para la búsqueda de fuentes bibliográficas, incluyendo tipos de fuente, cuartiles SCImago, rangos de APC, estado de acceso abierto, tiempo de publicación, tipos de licencia y temas.

@apiParam {String} [source_types] Tipos de fuente utilizados para filtrar los resultados.
@apiParam {String} [scimago_quartiles] Cuartiles SCImago utilizados para filtrar las fuentes.
@apiParam {String} [apc_range] Rango de cargos por procesamiento de artículos (APC).
@apiParam {String} [status] Estado de acceso abierto utilizado para filtrar las fuentes.
@apiParam {String} [publication_time] Tiempo de publicación utilizado como filtro.
@apiParam {String} [license_type] Tipo de licencia utilizado para filtrar las fuentes.
@apiParam {String} [topics] Temas utilizados para filtrar las fuentes.

@apiSuccess {Object} source_types Tipos de fuente disponibles para filtrar.
@apiSuccess {Object} scimago_quartiles Cuartiles SCImago disponibles.
@apiSuccess {Object} apc_range Rango de cargos por procesamiento de artículos disponible.
@apiSuccess {Object} status Estados de acceso abierto disponibles.
@apiSuccess {Object} publication_time Rangos de tiempo de publicación disponibles.
@apiSuccess {Object} license_type Tipos de licencia disponibles.
@apiSuccess {Object} topics Temas disponibles para filtrar.
"""


@search_router.route("/sources/filters", methods=["GET"])
def get_search_sources_filters() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams.model_validate(request.args.to_dict())
        data = search_service.search_sources_available_filters(query_params)
        return jsonify(data), 200
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
