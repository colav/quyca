from typing import Tuple
from flask import Blueprint, request, jsonify, Response

from domain.models.base_model import QueryParams
from quyca.domain.services import api_expert_service, source_service

source_api_router = Blueprint("source_api_router", __name__)

"""
@api {get} /source/:source_id Get Source by ID
@apiName GetSourceById
@apiGroup Source
@apiVersion 1.0.0
@apiDescription Obtiene los detalles de una fuente específica utilizando su identificador único.

@apiParam {String} source_id Identificador único de la fuente.

@apiSuccessExample {json} Success-Response:
HTTP/1.1 200 OK
{
  "data": {
    "abbreviations": [],
    "addresses": [],
    "apc": {},
    "citations_count": [
      {
        "count": 69,
        "source": "openalex"
      }
    ],
    "copyright": {},
    "external_ids": [
      {
        "id": "0196-1497",
        "source": "issn"
      },
      {
        "id": "2331-1258",
        "source": "issn"
      }
    ],
    "id": "6850c7bac2459d408de7fca0",
    "keywords": [],
    "languages": [],
    "licenses": [],
    "names": [
      {
        "lang": "en",
        "name": "US Geological Survey Open-File Report",
        "source": "scimago"
      }
    ],
    "plagiarism_detection": false,
    "products_count": 6,
    "publisher": {
      "country_code": "US",
      "name": "US Geological Survey"
    },
    "ranking": [
      {
        "from_date": 1735707600,
        "order": 19654,
        "rank": "Q3",
        "source": "scimago Best Quartile",
        "to_date": 1767157200
      }
    ],
    "relations": [],
    "subjects": [
      {
        "source": "scimago",
        "subjects": [
          {
            "external_ids": [],
            "id": "",
            "name": "Geology"
          }
        ]
      }
    ],
    "types": [
      {
        "source": "scimago",
        "type": "journal"
      }
    ],
    "updated": [
      {
        "source": "scimago",
        "time": 1750124474
      }
    ],
    "waiver": {}
  }
}

@apiError (404) SourceNotFound The source with the specified ID was not found.

@apiErrorExample {json} Respuesta de error:
HTTP/1.1 404 Not Found
{
  "error": "Source not found"
}
"""


@source_api_router.route("/<source_id>", methods=["GET"])
def get_source_by_id(source_id: str) -> Response | Tuple[Response, int]:
    try:
        data = source_service.get_source_by_id(source_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


"""
@api {get} /source/:source_id/research/products Get Research Products by Source
@apiName GetResearchProducts
@apiGroup Source
@apiVersion 1.0.0
@apiDescription Obtiene una lista paginada de productos de investigación publicados en una fuente específica.

@apiParam {String} source_id Identificador único de la fuente.

@apiQuery {Number} [page=1] Número de página para la paginación.
@apiQuery {Number} [max=10] Número máximo de resultados por página.
@apiQuery {String} [sort] Campo de ordenación.

@apiSuccessExample {json} Respuesta exitosa:
HTTP/1.1 200 OK
{
  "data": [
    {
      "apc": {},
      "authors": [
        {
          "affiliations": [
            {
              "addresses": [
                {
                  "city": "Bogotá",
                  "country": "Colombia",
                  "country_code": "CO"
                }
              ],
              "end_date": -1,
              "external_ids": [
                {
                  "id": "https://ror.org/059yx9a68",
                  "source": "ror"
                }
              ],
              "id": "059yx9a68",
              "name": "Universidad Nacional de Colombia",
              "start_date": -1,
              "types": [
                {
                  "source": "ror",
                  "type": "Education"
                }
              ]
            }
          ],
          "external_ids": [
            {
              "id": "https://openalex.org/A5011035542",
              "source": "openalex"
            }
          ],
          "first_names": ["R", "B"],
          "full_name": "R B Hall",
          "id": "A5011035542",
          "last_names": ["Hall"],
          "ranking": [],
          "sex": ""
        }
      ],
      "authors_count": 0,
      "doi": "https://doi.org/10.3133/ofr7397",
      "id": "68ade9918c9a28c93c2696ac",
      "open_access": {},
      "source": {
        "external_ids": [
          {
            "id": "0196-1497",
            "source": "issn"
          }
        ],
        "id": "6850c7bac2459d408de7fca0",
        "name": "Antarctica A Keystone in a Changing World",
        "types": [
          {
            "source": "scimago",
            "type": "journal"
          }
        ],
        "updated": [
          {
            "source": "scimago",
            "time": 1750124474
          }
        ]
      },
      "titles": [
        {
          "lang": "en",
          "source": "openalex",
          "title": "Geology and mineral resources of central Antioquia Department (Zone IIA), Colombia"
        }
      ],
      "year_published": 1973
    }
  ],
  "meta": {
    "count": 6,
    "db_response_time_ms": 3,
    "page": 1,
    "size": 1
  }
}

@apiError (404) SourceNotFound The source with the specified ID was not found.

@apiErrorExample {json} Respuesta de error:
HTTP/1.1 404 Not Found
{
  "error": "Failed to retrieve research products"
}
"""


@source_api_router.route("/<source_id>/research/products", methods=["GET"])
def get_research_products(source_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = api_expert_service.get_works_by_source(source_id, query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 404
