from datetime import datetime
from typing import Tuple, Any
from zoneinfo import ZoneInfo

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from sentry_sdk import capture_exception
from werkzeug.datastructures import FileStorage

from quyca.application.services.staff_service import StaffService, StaffUploadError
from quyca.infrastructure.container import build_staff_service

staff_app_router = Blueprint("staff_app_router", __name__)

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


@staff_app_router.route("/staff", methods=["POST"])
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
