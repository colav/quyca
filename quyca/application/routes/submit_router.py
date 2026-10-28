from datetime import datetime
from typing import Tuple, Any
from zoneinfo import ZoneInfo

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from sentry_sdk import capture_exception
from werkzeug.datastructures import FileStorage

from quyca.domain.exceptions.project_file_exceptions import ProjectFileException
from quyca.domain.services.submit import ciarp_service, scienti_service, staff_service, submit_project_file_service

submit_router = Blueprint("submit_app_router", __name__)


@submit_router.route("/staff", methods=["POST"])
def submit_staff() -> Tuple[Response, int]:
    try:
        try:
            verify_jwt_in_request()
            claims: dict[str, Any] = get_jwt()
        except Exception:
            return jsonify({"success": False, "msg": "Token inválido o expirado"}), 401

        file: FileStorage | None = request.files.get("file")
        if file is None:
            return jsonify({"success": False, "msg": "Archivo requerido"}), 400

        upload_date = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y %H:%M")

        result, status = staff_service.handle_staff_upload(file, claims, upload_date)
        return jsonify(result), status

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@submit_router.route("/ciarp", methods=["POST"])
def submit_ciarp() -> Tuple[Response, int]:
    try:
        try:
            verify_jwt_in_request()
            claims = get_jwt()
        except Exception:
            return jsonify({"success": False, "msg": "Token inválido o expirado"}), 401

        file = request.files.get("file")
        if file is None:
            return jsonify({"success": False, "msg": "Archivo requerido"}), 400

        upload_date = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y %H:%M")

        result, status = ciarp_service.handle_ciarp_upload(file, claims, upload_date)
        return jsonify(result), status

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@submit_router.route("/scienti", methods=["POST"])
def submit_scienti() -> Tuple[Response, int]:
    try:
        try:
            verify_jwt_in_request()
            claims: dict[str, Any] = get_jwt()
        except Exception:
            return jsonify({"success": False, "msg": "Token inválido o expirado"}), 401

        file = request.files.get("file")
        if file is None:
            return jsonify({"success": False, "msg": "Archivo requerido"}), 400

        upload_date = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y %H:%M")

        result, status = scienti_service.handle_scienti_upload(file=file, claims=claims, upload_date=upload_date)
        return jsonify(result), status

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@submit_router.route("/project", methods=["POST"])
def validate_project_file() -> Response | Tuple[Response, int]:
    try:
        file = request.files.get("file")
        if file is None or not file.filename:
            raise ProjectFileException("Debe enviar el archivo en el campo 'file' (multipart/form-data).")
        data = submit_project_file_service.validate_project_file(file.stream, file.filename)
        return jsonify(data)
    except ProjectFileException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
