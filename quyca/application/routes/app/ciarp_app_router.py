from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any

from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import Blueprint, request, jsonify
from sentry_sdk import capture_exception

from quyca.infrastructure.container import build_ciarp_service
from quyca.application.services.ciarp_service import CiarpService

ciarp_app_router = Blueprint("ciarp_app_router", __name__)

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


@ciarp_app_router.route("/ciarp", methods=["POST"])
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
