from datetime import datetime
from typing import Tuple
from zoneinfo import ZoneInfo
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import Blueprint, request, jsonify, Response
from infrastructure.container import build_staff_service
from domain.services.staff_service import StaffService

staff_app_router = Blueprint("staff_app_router", __name__)
"""
@api {post} /app/staff
@apiName PostStaffFile
@apiGroup Staff
@apiVersion 1.0.0
@apiDescription Permite subir un archivo Excel con la información de personal (staff).  
El sistema valida el archivo, genera un reporte PDF (en base64) y, si no hay errores, lo guarda en Google Drive.

@apiHeader {String} Authorization Token JWT en el header con el formato: "Bearer <token>".

@apiBody {File} file Archivo Excel (.xlsx) con la información del staff.  
Debe incluir las columnas requeridas: tipo_documento, identificación, primer_apellido, nombres, tipo_contrato, jornada_laboral, fecha_nacimiento, fecha_inicial_vinculación, código_unidad_académica, unidad_académica.

@apiSuccess {Boolean} success Indica si la validación fue exitosa (no hay errores).
@apiSuccess {Number} errores Número de errores encontrados en el archivo.
@apiSuccess {Number} duplicados Número de registros duplicados detectados.
@apiSuccess {String} pdf_base64 Reporte en formato PDF codificado en Base64.

@apiSuccessExample {json} Respuesta exitosa:
HTTP/1.1 200 OK
{
    "success": true,
    "errores": 0,
    "duplicados": 2,
    "pdf_base64": "JVBERi0xLjQKJ..."
}

@apiError {Boolean} success Indica si la validación falló.
@apiError {String} msg Mensaje de error.

@apiErrorExample {json} Respuesta error por token inválido:
HTTP/1.1 401 Unauthorized
{
    "success": false,
    "msg": "Token inválido o expirado"
}

@apiErrorExample {json} Respuesta error por archivo faltante:
HTTP/1.1 400 Bad Request
{
    "success": false,
    "msg": "Archivo requerido"
}

@apiErrorExample {json} Respuesta error por errores en el archivo:
HTTP/1.1 400 Bad Request
{
    "success": false,
    "errores": 3,
    "duplicados": 1,
    "pdf_base64": "JVBERi0xLjQKJ..."
}
"""


@staff_app_router.route("/staff", methods=["POST"])
def submit_staff() -> Tuple[Response, int]:
    try:
        verify_jwt_in_request()
        claims = get_jwt()
    except Exception:
        return jsonify({"success": False, "msg": "Token inválido o expirado"}), 401

    auth_header = request.headers.get("Authorization", None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"success": False, "msg": "Token no encontrado en headers"}), 401

    token_from_header = auth_header.split(" ")[1]
    file = request.files.get("file")
    upload_date = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y %H:%M")

    process_usecase, save_usecase, user_repo = build_staff_service()
    service = StaffService(process_usecase, save_usecase, user_repo)

    result, status = service.handle_staff_upload(file, claims, token_from_header, upload_date)
    return jsonify(result), status
