from typing import Generator

from flask import Blueprint, Response

from quyca.api.helpers import parse_query_params, register_error_handlers
from quyca.services import apc_service

apc_router = Blueprint("apc_api_router", __name__)
register_error_handlers(apc_router)


@apc_router.route("/search", methods=["GET"])
def get_apc_csv_by_search() -> Response:
    return _csv_response(apc_service.get_apc_csv_by_search(parse_query_params().keywords), "search.csv")


@apc_router.route("/person/<person_id>", methods=["GET"])
def get_apc_csv_by_person(person_id: str) -> Response:
    return _csv_response(apc_service.get_apc_csv_by_person(person_id), "person.csv")


@apc_router.route("/affiliation/<affiliation_id>", methods=["GET"])
def get_apc_csv_by_affiliation(affiliation_id: str) -> Response:
    return _csv_response(apc_service.get_apc_csv_by_affiliation(affiliation_id), "affiliation.csv")


def _csv_response(csv_rows: Generator[str, None, None], filename: str) -> Response:
    return Response(
        csv_rows, content_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
