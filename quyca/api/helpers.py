from typing import Iterable

from flask import Blueprint, Response, current_app, jsonify, request
from pydantic import ValidationError
from sentry_sdk import capture_exception
from werkzeug.exceptions import HTTPException

from quyca.exceptions.invalid_param_exception import InvalidParamException
from quyca.exceptions.not_entity_exception import NotEntityException
from quyca.models.base_model import QueryParams

CSV_CONTENT_TYPE = "text/csv; charset=utf-8"
XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def parse_query_params() -> QueryParams:
    try:
        return QueryParams.model_validate(request.args.to_dict())
    except ValidationError as e:
        raise InvalidParamException(str(e)) from e


def file_response(content: Iterable[str] | bytes, filename: str, content_type: str) -> Response:
    """Download response; a generator is streamed while it is produced."""
    return Response(
        content, content_type=content_type, headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def register_error_handlers(blueprint: Blueprint) -> None:
    """Client errors answer 400 with their message, missing entities 404; anything else is reported to Sentry and answers 500."""

    @blueprint.errorhandler(InvalidParamException)
    def handle_invalid_param(error: InvalidParamException) -> tuple[Response, int]:
        return jsonify({"error": str(error)}), 400

    @blueprint.errorhandler(NotEntityException)
    def handle_not_entity(error: NotEntityException) -> tuple[Response, int]:
        return jsonify({"error": str(error)}), 404

    @blueprint.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> HTTPException | tuple[Response, int]:
        if isinstance(error, HTTPException):
            return error
        current_app.logger.exception(error)
        capture_exception(error)
        return jsonify({"error": "Internal server error"}), 500
