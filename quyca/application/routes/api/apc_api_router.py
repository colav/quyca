import csv
import io
from typing import Any, Generator, Iterable, Mapping, Sequence, Tuple
from pymongo.command_cursor import CommandCursor

from flask import Blueprint, request, jsonify, Response
from sentry_sdk import capture_exception

from quyca.domain.models.base_model import QueryParams
from quyca.infrastructure.mongo import database

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
        cursor: CommandCursor[dict[str, Any]] = database["works"].aggregate(pipeline)
        rows: list[dict[str, Any]] = list(cursor)
        fieldnames = [
            "work_doi",
            "work_title",
            "source_name",
            "source_apc_value",
            "source_apc_currency",
            "work_apc_value",
            "work_apc_currency",
        ]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, escapechar="\\", quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)
        csv_data: str = output.getvalue()
        response = Response(csv_data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=search.csv"
        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@apc_api_router.route("/person/<person_id>", methods=["GET"])
def apc_person(person_id: str) -> Response | Tuple[Response, int]:
    try:
        pipeline: Sequence[Mapping[str, Any]] = [
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

        cursor: CommandCursor[dict[str, Any]] = database["works"].aggregate(pipeline)
        rows: list[dict[str, Any]] = list(cursor)

        fieldnames = [
            "work_doi",
            "work_title",
            "source_name",
            "source_apc_value",
            "source_apc_currency",
            "work_apc_value",
            "work_apc_currency",
        ]

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            escapechar="\\",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        writer.writerows(rows)

        csv_data: str = output.getvalue()
        response = Response(csv_data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=person.csv"
        return response

    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@apc_api_router.route("/affiliation/<affiliation_id>", methods=["GET"])
def apc_affiliation(affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        pipeline: Sequence[Mapping[str, Any]] = [
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
