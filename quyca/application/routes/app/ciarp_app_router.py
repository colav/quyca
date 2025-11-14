from datetime import datetime
from zoneinfo import ZoneInfo
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import Blueprint, request, jsonify
from infrastructure.container import build_ciarp_service
from domain.services.ciarp_service import CiarpService

ciarp_app_router = Blueprint("ciarp_app_router", __name__)

"""
@api {post} /app/submit/ciarp Upload CIARP Excel file
@apiName SubmitCiarp
@apiGroup CIARP
@apiVersion 1.0.0

@apiDescription
Uploads a CIARP Excel file for validation and generates a data quality report (PDF + annotated Excel).  
The request must include a valid JWT token in the Authorization header.

@apiHeader {String} Authorization JWT token in the format `Bearer <token>`.

@apiBody {File} file Excel file to be validated (format `.xlsx`).

@apiSuccess (200) {Boolean} success Indicates if the process was successful.
@apiSuccess (200) {Number} errores Number of validation errors found.
@apiSuccess (200) {Number} duplicados Number of duplicated records found.
@apiSuccess (200) {String} pdf_base64 Base64 string of the generated PDF report (if available).
@apiSuccess (200) {String} msg Process result message.

@apiError (400) {Boolean} success `false`
@apiError (400) {String} msg "Archivo requerido" or "El archivo cargado está vacío. Verifique que contenga información."
@apiError (401) {String} msg "Token inválido o expirado" or "Token no encontrado en headers."
@apiError (422) {String} msg "El archivo enviado no cumple con el formato requerido de columnas"
@apiError (500) {String} msg "Fallo al enviar correo" or internal processing errors.

@apiExample {curl} Example usage:
curl -X POST https://api.quyca.co/app/submit/ciarp \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1Ni..." \
    -F "file=@/path/to/ciarp.xlsx"

@apiSuccessExample {json} Success Response (200):
{
    "success": true,
    "errores": 0,
    "duplicados": 1,
    "pdf_base64": "JVBERi0xLjQKJ...",
    "msg": "Archivo procesado correctamente"
}

@apiErrorExample {json} Invalid Columns (422):
{
    "success": false,
    "msg": "El archivo enviado no cumple con el formato requerido de columnas",
    "detalles": ["Columna faltante: código_unidad_académica"]
}
"""


@ciarp_app_router.route("/ciarp", methods=["POST"])
def submit_ciarp():
    try:
        verify_jwt_in_request()
        claims = get_jwt()
    except Exception:
        return jsonify({"success": False, "msg": "Token inválido o expirado"}), 401

    auth_header = request.headers.get("Authorization", None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"success": False, "msg": "Token inválido o expirado"}), 401

    token_from_header = auth_header.split(" ")[1]
    file = request.files.get("file")
    upload_date = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y %H:%M")

    process_usecase, save_usecase, user_repo = build_ciarp_service()
    service = CiarpService(process_usecase, save_usecase, user_repo)

    result, status = service.handle_ciarp_upload(file, claims, token_from_header, upload_date)
    return jsonify(result), status
