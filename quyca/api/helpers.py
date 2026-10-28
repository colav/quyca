from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError
from sentry_sdk import capture_exception
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers.response import Response

from quyca.exceptions.invalid_param_exception import InvalidParamException
from quyca.models.base_model import QueryParams


def parse_query_params() -> QueryParams:
    try:
        return QueryParams.model_validate(request.args.to_dict())
    except ValidationError as e:
        raise InvalidParamException(str(e)) from e


def register_error_handlers(blueprint: Blueprint) -> None:
    """Client errors answer 400 with their message; anything else is reported to Sentry and answers 500."""

    @blueprint.errorhandler(InvalidParamException)
    def handle_invalid_param(error: InvalidParamException) -> tuple[Response, int]:
        return jsonify({"error": str(error)}), 400

    @blueprint.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> HTTPException | tuple[Response, int]:
        if isinstance(error, HTTPException):
            return error
        current_app.logger.exception(error)
        capture_exception(error)
        return jsonify({"error": "Internal server error"}), 500
