from typing import Tuple
from flask import Blueprint, request, jsonify, Response
from sentry_sdk import capture_exception

from flask_jwt_extended import set_access_cookies, unset_jwt_cookies

from quyca.domain.exceptions.not_entity_exception import NotEntityException
from quyca.infrastructure.repositories.user_repository import UserRepositoryMongo
from quyca.infrastructure.security.jwt_token_service import JwtTokenService
from quyca.application.usecases.login_user import LoginUserUseCase

user_auth_app_router = Blueprint("user_auth_app_router", __name__)

"""
@api {post} /app/login Iniciar sesión
@apiName PostLoginUser
@apiGroup Authentication
@apiVersion 1.0.0

@apiDescription
Autentica con email y contraseña. Si es válido:
- Responde JSON con datos del usuario (sin token)
- Setea cookie HttpOnly `access_token_cookie` con el JWT

@apiBody {String} email
@apiBody {String} password

@apiSuccess (200) {Boolean} success true
@apiSuccess (200) {String} _id
@apiSuccess (200) {String} institution
@apiSuccess (200) {String} role

@apiSuccessExample {json} 200 OK
{
  "success": true,
  "_id": "03bp5hc83",
  "institution": "Universidad de Antioquia",
  "role": "admin"
}

@apiError (400) {Boolean} success false
@apiError (400) {String} msg "correo y contraseña requeridos"
@apiError (401) {Boolean} success false
@apiError (401) {String} msg "Credenciales inválidas"
@apiError (403) {Boolean} success false
@apiError (403) {String} msg "El usuario está desactivado..."
@apiError (500) {Boolean} success false
@apiError (500) {String} msg "Error interno del servidor"
"""


@user_auth_app_router.route("/login", methods=["POST"])
def login() -> Tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify({"success": False, "msg": "correo y contraseña requeridos"}), 400

        repo = UserRepositoryMongo()
        token_service = JwtTokenService()
        usecase = LoginUserUseCase(user_repo=repo, token_service=token_service)

        result = usecase.execute(email, password)

        status_code = 200 if result.get("success") else 401

        token = result.get("access_token", "")
        response_body = {**result}

        response_body.pop("access_token", None)

        response = jsonify(response_body)
        if status_code == 200 and token:
            set_access_cookies(response, token)

        return response, status_code

    except NotEntityException as e:
        msg = str(e)

        if "desactivada" in msg.lower():
            status = 403
        else:
            status = 401

        return jsonify({"success": False, "msg": msg}), status

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": str("Error interno del servidor")}), 500


"""
@api {post} /app/logout Cerrar sesión
@apiName PostLogoutUser
@apiGroup Authentication
@apiVersion 1.0.0

@apiDescription
Cierra sesión limpiando las cookies JWT (unset_jwt_cookies).
No requiere enviar token en el body.

@apiSuccess (200) {Boolean} success true
@apiSuccess (200) {String} msg "Sesión cerrada correctamente"

@apiError (500) {Boolean} success false
@apiError (500) {String} msg "Error interno del servidor"
"""


@user_auth_app_router.route("/logout", methods=["POST"])
def logout() -> Tuple[Response, int]:
    try:
        response = jsonify({"success": True, "msg": "Sesión cerrada correctamente"})
        unset_jwt_cookies(response)

        return response, 200

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": f"Error interno del servidor"}), 500
