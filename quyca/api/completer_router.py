from typing import Tuple

from flask import Blueprint, jsonify, Response
from sentry_sdk import capture_exception

from quyca.repositories import completers

completer_router = Blueprint("completer_app_router", __name__)


@completer_router.route("/person/<text>", methods=["GET"])
def get_person_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.person_completer(text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@completer_router.route("/affiliations/institution/<text>", methods=["GET"])
def get_institution_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.affiliations_completer("institution", text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@completer_router.route("/affiliations/group/<text>", methods=["GET"])
def get_group_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.affiliations_completer("group", text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@completer_router.route("/affiliations/department/<text>", methods=["GET"])
def get_department_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.affiliations_completer("department", text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@completer_router.route("/affiliations/faculty/<text>", methods=["GET"])
def get_faculty_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.affiliations_completer("faculty", text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@completer_router.route("/sources/<text>", methods=["GET"])
def get_source_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.source_completer(text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
