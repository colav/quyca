from typing import Tuple
from flask import Blueprint, request, jsonify, Response
from sentry_sdk import capture_exception

from domain.services import auth_service
from infrastructure.repositories.user_repository import UserRepositoryMongo

user_auth_app_router = Blueprint("user_auth_app_router", __name__)

"""
@api {post} /app/login
@apiName PostLoginUser
@apiGroup Autenticación
@apiVersion 1.0.0
@apiDescription Permite autenticar un usuario con su correo y contraseña.
Si las credenciales son válidas, retorna un token JWT junto con el rol del usuario.

@apiBody {String} email Correo del usuario.
@apiBody {String} password Contraseña del usuario.

@apiSuccess {Boolean} success Indica si la autenticación fue exitosa.
@apiSuccess {String} rolID Número id asociado a la entidad.
@apiSuccess {String} access_token Token JWT generado.

@apiSuccessExample {json} Respuesta exitosa:
HTTP/1.1 200 OK
{
    "success": true,
    "rolID": "admin",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR..."
}

@apiError {Boolean} success Indica si la autenticación falló.
@apiError {String} msg Mensaje de error.

@apiErrorExample {json} Respuesta error credenciales inválidas:
HTTP/1.1 401 Unauthorized
{
    "success": false
}

@apiErrorExample {json} Respuesta error datos faltantes:
HTTP/1.1 400 Bad Request
{
    "success": false,
    "msg": "correo y contraseña requeridos"
}
"""


@user_auth_app_router.route("/login", methods=["POST"])
def login() -> Tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        email = (data.get("email") or "").strip()
        password = data.get("password")

        if not email or not password:
            return jsonify({"success": False, "msg": "correo y contraseña requeridos"}), 400

        repo = UserRepositoryMongo()
        result = auth_service.authenticate_user(email, password, repo)
        success = result.get("success")
        status_code = 200 if success else 401
        return jsonify(result), status_code
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": str(e)}), 500


"""
@api {post} /app/logout
@apiName PostLogoutUser
@apiGroup Autenticación
@apiVersion 1.0.0
@apiDescription Permite cerrar la sesión de un usuario invalidando su token JWT.  
Si el token es válido, se elimina de la base de datos.

@apiBody {String} token Token JWT que se desea invalidar.

@apiSuccess {Boolean} success Indica si el cierre de sesión fue exitoso.
@apiSuccess {String} msg Mensaje de confirmación.

@apiSuccessExample {json} Respuesta exitosa:
HTTP/1.1 200 OK
{
    "success": true,
    "msg": "Sesión cerrada correctamente"
}
"""


@user_auth_app_router.route("/logout", methods=["POST"])
def logout() -> Tuple[Response, int]:
    try:
        data = request.get_json()
        token = data.get("token")

        if not token:
            return jsonify({"msg": "Token requerido", "success": False}), 400
        repo = UserRepositoryMongo()
        result = auth_service.logout_user(token, repo)
        status_code = 200 if result.get("success") else 401
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500
