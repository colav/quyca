import csv
import io
from typing import Any, Generator, Iterable, Tuple

from flask import Blueprint, request, jsonify, Response
from sentry_sdk import capture_exception

from domain.models.base_model import QueryParams
from infrastructure.mongo import database

apc_api_router = Blueprint("apc_api_router", __name__)


@apc_api_router.route("/search", methods=["GET"])
def apc_search() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        pipeline: list[dict[str, Any]] = []
        if query_params.keywords:
            pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}]
        pipeline += [
            {
                "$project": {
                    "_id": 0,
                    "work_doi": "$doi",
                    "work_title": {"$first": "$titles.title"},
                    "source_name": "$source.name",
                    "source_apc_value": "$source.apc.charges",
                    "source_apc_currency": "$source.apc.currency",
                    "work_apc_currency": "$apc.paid.currency",
                    "work_apc_value": "$apc.paid.value",
                }
            }
        ]
        data = database["works"].aggregate(pipeline)
        fieldnames = [
            "work_doi",
            "work_title",
            "source_name",
            "source_apc_value",
            "source_apc_currency",
            "work_apc_value",
            "work_apc_currency",
        ]
        data = list(data)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, escapechar="\\", quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(data)
        data = output.getvalue()
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=search.csv"
        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@apc_api_router.route("/person/<person_id>", methods=["GET"])
def apc_person(person_id: str) -> Response | Tuple[Response, int]:
    try:
        pipeline = [
            {"$match": {"authors.id": person_id}},
            {
                "$project": {
                    "_id": 0,
                    "work_doi": "$doi",
                    "work_title": {"$first": "$titles.title"},
                    "source_name": "$source.name",
                    "source_apc_value": "$source.apc.charges",
                    "source_apc_currency": "$source.apc.currency",
                    "work_apc_currency": "$apc.paid.currency",
                    "work_apc_value": "$apc.paid.value",
                }
            },
        ]

        data = database["works"].aggregate(pipeline)

        fieldnames = [
            "work_doi",
            "work_title",
            "source_name",
            "source_apc_value",
            "source_apc_currency",
            "work_apc_value",
            "work_apc_currency",
        ]

        data = list(data)
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            escapechar="\\",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        writer.writerows(data)

        data = output.getvalue()
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=person.csv"
        return response

    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@apc_api_router.route("/affiliation/<affiliation_id>", methods=["GET"])
def apc_affiliation(affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        pipeline = [
            {"$match": {"authors.affiliations.id": affiliation_id}},
            {
                "$project": {
                    "_id": 0,
                    "work_doi": "$doi",
                    "work_title": {"$first": "$titles.title"},
                    "source_name": "$source.name",
                    "source_apc_value": "$source.apc.charges",
                    "source_apc_currency": "$source.apc.currency",
                    "work_apc_currency": "$apc.paid.currency",
                    "work_apc_value": "$apc.paid.value",
                }
            },
        ]

        cursor = database["works"].aggregate(pipeline)

        fieldnames = [
            "work_doi",
            "work_title",
            "source_name",
            "source_apc_value",
            "source_apc_currency",
            "work_apc_value",
            "work_apc_currency",
        ]

        def generate_csv(cursor: Iterable[Any], fieldnames: list[str]) -> Generator[str, None, None]:
            yield ",".join(fieldnames) + "\n"
            for doc in cursor:
                row = {field: doc.get(field, "") for field in fieldnames}
                yield ",".join(map(str, row.values())) + "\n"

        return Response(
            generate_csv(cursor, fieldnames),
            content_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=affiliation.csv"},
        )

    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
