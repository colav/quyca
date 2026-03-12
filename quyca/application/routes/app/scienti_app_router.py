from datetime import datetime
from typing import Any, Tuple
from zoneinfo import ZoneInfo

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from sentry_sdk import capture_exception

from quyca.infrastructure.container import build_scienti_service
from quyca.domain.services.scienti_service import ScientiService

scienti_app_router = Blueprint("scienti_app_router", __name__)

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


@scienti_app_router.route("/scienti", methods=["POST"])
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
