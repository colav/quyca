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
from quyca.domain.services.scienti_service import ScientiService
from quyca.domain.services.submit import submit_project_service
from quyca.infrastructure.container import build_ciarp_service, build_scienti_service, build_staff_service

submit_app_router = Blueprint("submit_app_router", __name__)

"""
@api {post} /app/submit/staff Subir archivo Staff (.xlsx)
@apiName SubmitStaff
@apiGroup Staff
@apiVersion 1.0.0

@apiDescription
Sube un Excel de Staff para validación, genera reporte (PDF + Excel anotado) y envía notificación.
Auth por cookie HttpOnly `access_token_cookie`.

@apiHeader (Auth Cookie) {String} access_token_cookie Cookie JWT HttpOnly.

@apiBody {File} file Archivo Excel `.xlsx`.

@apiSuccess (200) {Boolean} success
@apiSuccess (200) {Number} errors
@apiSuccess (200) {Number} duplicates
@apiSuccess (200) {String} pdf_base64
@apiSuccess (200) {String} msg

@apiError (400) {Boolean} success false
@apiError (400) {String} msg "Archivo requerido" | "El archivo cargado está vacío. Verifique que contenga información."
@apiError (401) {Boolean} success false
@apiError (401) {String} msg "Token inválido o expirado"
@apiError (422) {Boolean} success false
@apiError (422) {String} msg "El archivo enviado no cumple con el formato requerido de columnas"
@apiError (500) {String} msg "Error interno del servidor"
"""


@submit_app_router.route("/staff", methods=["POST"])
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


"""
@api {post} /app/submit/ciarp Subir archivo CIARP (.xlsx)
@apiName SubmitCiarp
@apiGroup CIARP
@apiVersion 1.0.0

@apiDescription
Sube un Excel CIARP para validación y genera reporte de calidad (PDF + anotaciones).
La autenticación se maneja con cookie HttpOnly `access_token_cookie` (no se envía token en JSON).

@apiHeader (Auth Cookie) {String} access_token_cookie Cookie JWT HttpOnly (enviada automáticamente por el navegador).

@apiBody {File} file Archivo Excel `.xlsx`.

@apiSuccess (200) {Boolean} success
@apiSuccess (200) {Number} errors
@apiSuccess (200) {Number} duplicates
@apiSuccess (200) {String} pdf_base64
@apiSuccess (200) {String} msg

@apiError (400) {Boolean} success false
@apiError (400) {String} msg "Archivo requerido" | "El archivo cargado está vacío. Verifique que contenga información."
@apiError (401) {Boolean} success false
@apiError (401) {String} msg "Token inválido o expirado"
@apiError (422) {Boolean} success false
@apiError (422) {String} msg "El archivo enviado no cumple con el formato requerido de columnas"
@apiError (500) {String} msg "Error interno del servidor"
"""


@submit_app_router.route("/ciarp", methods=["POST"])
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


"""
@api {post} /app/submit/scienti Subir comprimido SCIENTI
@apiName SubmitScienti
@apiGroup SCIENTI
@apiVersion 1.0.0

@apiDescription
Sube un archivo comprimido de SCIENTI para validación/procesamiento.
Auth por cookie HttpOnly `access_token_cookie`.

@apiHeader (Auth Cookie) {String} access_token_cookie Cookie JWT HttpOnly.

@apiBody {File} file Archivo comprimido (.zip, .rar, .7z, .tar, .gz, .tgz, .bz2, .tar.gz, .tar.bz2).

@apiSuccess (200) {Boolean} success
@apiSuccess (200) {String} msg
@apiSuccess (200) {String} upload_date
@apiSuccess (200) {String} file_msg

@apiError (400) {Boolean} success false
@apiError (400) {String} msg "Archivo requerido"
@apiError (401) {Boolean} success false
@apiError (401) {String} msg "Token inválido o expirado"
@apiError (415) {Boolean} success false
@apiError (415) {String} msg "Tipo de archivo no permitido..."
@apiError (500) {String} msg "Error interno del servidor"
"""


@submit_app_router.route("/scienti", methods=["POST"])
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


"""
@api {post} /app/project/validate Validate projects file
@apiName ValidateProjectFile
@apiGroup Project
@apiVersion 1.0.0
@apiDescription Valida el archivo Excel de proyectos institucionales (formato v1.0) y devuelve el reporte de errores y advertencias.
 
@apiBody {File} file Archivo .xlsx enviado como multipart/form-data.
"""
 
 
@submit_app_router.route("/project", methods=["POST"])
def validate_project_file() -> Response | Tuple[Response, int]:
    try:
        file = request.files.get("file")
        if file is None or not file.filename:
            raise ProjectFileException("Debe enviar el archivo en el campo 'file' (multipart/form-data).")
        data = submit_project_service.validate_project_file(file.stream, file.filename)
        return jsonify(data)
    except ProjectFileException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400