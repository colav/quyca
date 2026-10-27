from datetime import datetime
from typing import Tuple, Any
from zoneinfo import ZoneInfo

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from sentry_sdk import capture_exception
from werkzeug.datastructures import FileStorage

from quyca.application.services.ciarp_service import CiarpService
from quyca.application.services.staff_service import StaffService, StaffUploadError
from quyca.domain.exceptions.project_file_exceptions import ProjectFileException
from quyca.domain.services.submit.scienti_service import ScientiService
from quyca.domain.services.submit import submit_project_file_service
from quyca.infrastructure.container import build_ciarp_service, build_scienti_service, build_staff_service

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

        process_usecase, save_usecase = build_staff_service()
        service = StaffService(process_usecase, save_usecase)

        outcome = service.handle_staff_upload(file, claims, upload_date)

        if outcome.error == StaffUploadError.UNAUTHORIZED:
            return jsonify(outcome.payload), 401

        if outcome.error == StaffUploadError.UNPROCESSABLE_ENTITY:
            return jsonify(outcome.payload), 422

        if outcome.error == StaffUploadError.BAD_REQUEST:
            return jsonify(outcome.payload), 400

        if outcome.error == StaffUploadError.INTERNAL_ERROR:
            return jsonify(outcome.payload), 500

        return jsonify(outcome.payload), 200

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@submit_router.route("/ciarp", methods=["POST"])
def submit_ciarp() -> tuple[Any, int]:
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

        process_usecase, save_usecase = build_ciarp_service()
        service = CiarpService(process_usecase, save_usecase)

        result, status = service.handle_ciarp_upload(file, claims, upload_date)
        return jsonify(result), status

    except Exception as e:
        capture_exception(e)
        return jsonify({"succes": False, "msg": "Error interno del servidor"}), 500


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

        service: ScientiService = build_scienti_service()

        result, status = service.handle_scienti_upload(file=file, claims=claims, upload_date=upload_date)

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
