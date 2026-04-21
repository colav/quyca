from typing import Any
from flask import Blueprint, jsonify
from sentry_sdk import capture_exception
from quyca.infrastructure.container import build_get_me_usecase

me_app_router = Blueprint("me_app_router", __name__)


"""
@api {get} /app/me Estado de sesión
@apiName GetMe
@apiGroup Authentication
@apiVersion 1.0.0

@apiDescription
Retorna el estado de la sesión actual leyendo el JWT desde cookie HttpOnly `access_token_cookie`.
- 200 si la sesión está activa
- 401 si no hay sesión o el token es inválido/expirado

@apiHeader (Auth Cookie) {String} access_token_cookie Cookie JWT HttpOnly.

@apiSuccess (200) {String} status "sesion_activa"
@apiSuccess (200) {String} msg "Sesión activa"
@apiSuccess (200) {Object} user
@apiSuccess (200) {String} user._id
@apiSuccess (200) {String} user.institution
@apiSuccess (200) {String} user.role
@apiSuccess (200) {String} user.email

@apiError (401) {String} status "sesion_no_iniciada" | "token_expirado"
@apiError (401) {String} msg
@apiError (500) {Boolean} success false
@apiError (500) {String} msg "Error interno del servidor"
"""


@me_app_router.route("/me", methods=["GET"])
def me() -> tuple[Any, int]:
    try:
        usecase = build_get_me_usecase()
        result = usecase.execute()

        status_code = 200 if result.status == "sesion_activa" else 401

        payload: dict[str, Any] = {"status": result.status, "msg": result.msg}
        if result.user is not None:
            payload["user"] = result.user

        return jsonify(payload), status_code
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500
