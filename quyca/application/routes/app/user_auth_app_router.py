from typing import Tuple
from flask import Blueprint, request, jsonify, Response
from sentry_sdk import capture_exception
from domain.exceptions.not_entity_exception import NotEntityException
from domain.services import auth_service
from infrastructure.repositories.user_repository import UserRepositoryMongo

user_auth_app_router = Blueprint("user_auth_app_router", __name__)

"""
@api {post} /app/login
@apiName PostLoginUser
@apiGroup Authentication
@apiVersion 1.0.0
@apiDescription Allows authenticating a user using their email and password.
If the credentials are valid, it returns a JWT token along with the user's role.

@apiBody {String} email User email.
@apiBody {String} password User password.

@apiSuccess {Boolean} success Indicates whether the authentication was successful.
@apiSuccess {String} rorID ID number associated with the entity.
@apiSuccess {String} access_token Generated JWT token.

@apiSuccessExample {json} Successful Response:
HTTP/1.1 200 OK
{
    "success": true,
    "rorID": "admin",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR..."
}

@apiError {Boolean} success Indicates that authentication failed.
@apiError {String} msg Error message.

@apiErrorExample {json} Error Response - Invalid Credentials:
HTTP/1.1 401 Unauthorized
{
    "success": false
}

@apiErrorExample {json} Error Response - Missing Fields:
HTTP/1.1 400 Bad Request
{
    "success": false,
    "msg": "email and password are required"
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

        if not result.get("success"):
            return jsonify(result), 401

        return jsonify(result), 200

    except NotEntityException as e:
        msg = str(e)
        status = 403 if "desactivada" in msg.lower() else 401
        return jsonify({"success": False, "msg": msg}), status

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": str(e)}), 500


"""
@api {post} /app/logout
@apiName PostLogoutUser
@apiGroup Authentication
@apiVersion 1.0.0
@apiDescription Allows logging out a user by invalidating their JWT token.  
If the token is valid, it is removed from the database.

@apiBody {String} token JWT token to be invalidated.

@apiSuccess {Boolean} success Indicates whether the logout was successful.
@apiSuccess {String} msg Confirmation message.

@apiSuccessExample {json} Successful Response:
HTTP/1.1 200 OK
{
    "success": true,
    "msg": "Session closed successfully"
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
