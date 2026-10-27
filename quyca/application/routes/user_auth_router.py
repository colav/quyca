from typing import Tuple
from flask import Blueprint, request, jsonify, Response
from sentry_sdk import capture_exception

from flask_jwt_extended import set_access_cookies, unset_jwt_cookies

from quyca.domain.exceptions.not_entity_exception import NotEntityException
from quyca.infrastructure.repositories.user_repository import UserRepositoryMongo
from quyca.infrastructure.security.jwt_token_service import JwtTokenService
from quyca.application.usecases.login_user import LoginUserUseCase

user_auth_router = Blueprint("user_auth_app_router", __name__)


@user_auth_router.route("/login", methods=["POST"])
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


@user_auth_router.route("/logout", methods=["POST"])
def logout() -> Tuple[Response, int]:
    try:
        response = jsonify({"success": True, "msg": "Sesión cerrada correctamente"})
        unset_jwt_cookies(response)

        return response, 200

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": f"Error interno del servidor"}), 500
