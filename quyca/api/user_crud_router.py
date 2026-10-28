from typing import Any
from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from sentry_sdk import capture_exception
from quyca.services import user_service
from quyca.exceptions.not_entity_exception import NotEntityException

user_crud_router = Blueprint("user_crud_app_router", __name__)


def check_admin_permission() -> tuple[dict[str, Any] | None, int | None]:
    """Validates JWT exists and role is admin."""
    try:
        verify_jwt_in_request()
    except Exception:
        return {
            "success": False,
            "msg": "Token no proporcionado o inválido. Por favor, inicia sesión nuevamente.",
        }, 401

    claims = get_jwt()
    user_role = claims.get("role")

    if not isinstance(user_role, str) or user_role.lower() != "admin":
        return {"success": False, "msg": "Permiso denegado: No pueden realizar esta acción."}, 403

    email = get_jwt_identity()
    if not isinstance(email, str) or not email.strip():
        return {"success": False, "msg": "Identidad de sesión inválida"}, 401

    return None, None


@user_crud_router.route("/admin/users/<email>", methods=["POST"])
def create_user(email: str) -> tuple[Any, int]:
    """Creates a user (admin-only)."""
    error_response, status = check_admin_permission()
    if error_response is not None and status is not None:
        return jsonify(error_response), status

    try:
        data = request.get_json()
        email = email.strip().lower()
        institution = data.get("institution")
        ror_id = data.get("ror_id")
        role = data.get("role")

        result = user_service.create_user(email, institution, ror_id, role, data)

        if not result.get("success") and "ya existe" in result.get("msg", "").lower():
            return jsonify(result), 409

        return jsonify(result), 201
    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 400
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@user_crud_router.route("/admin/users", methods=["GET"])
def list_users() -> tuple[Any, int]:
    """Lists users (admin-only, excludes admins)."""
    error_response, status = check_admin_permission()
    if error_response is not None and status is not None:
        return jsonify(error_response), status

    try:
        result = user_service.get_all_users()
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@user_crud_router.route("/admin/users/<email>", methods=["DELETE"])
def deactivate_user(email: str) -> tuple[Any, int]:
    error_response, status = check_admin_permission()
    if error_response is not None and status is not None:
        return jsonify(error_response), status

    try:
        email = email.strip().lower()
        result = user_service.deactivate_user(email)
        return jsonify(result), 200

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 404
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@user_crud_router.route("/admin/users/<email>/restore", methods=["PATCH"])
def activate_user(email: str) -> tuple[Any, int]:
    error_response, status = check_admin_permission()
    if error_response is not None and status is not None:
        return jsonify(error_response), status

    try:
        email = email.strip().lower()
        result = user_service.activate_user(email)
        return jsonify(result), 200

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 404
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@user_crud_router.route("/admin/users/<email>", methods=["PATCH"])
def update_password(email: str) -> tuple[Any, int]:
    """Resets password and emails credentials (admin-only)."""
    error_response, status = check_admin_permission()
    if error_response is not None and status is not None:
        return jsonify(error_response), status

    try:
        email = email.strip().lower()

        result = user_service.update_password(email)
        return jsonify(result), 200
    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 400
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@user_crud_router.route("/admin/users/<email>", methods=["PUT"])
def edit_user(email: str) -> tuple[Any, int]:
    """Edits email and/or role (admin-only) with admin-safety rules."""
    error_response, status = check_admin_permission()
    if error_response is not None and status is not None:
        return jsonify(error_response), status

    try:
        old_email = email.strip().lower()
        data = request.get_json(force=True) or {}
        new_email = (data.get("email") or "").strip().lower()
        new_role = (data.get("role") or "").strip().lower()

        if not new_email and not new_role:
            return jsonify({"success": False, "msg": "Debes enviar al menos email o rol."}), 400

        result = user_service.update_user_info(old_email, new_email or old_email, new_role or "", data)
        if not result.get("success") and "role 'admin'" in result.get("msg", "").lower():
            return jsonify(result), 403
        return jsonify(result), (200 if result.get("success") else 400)

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 404
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@user_crud_router.route("/users/<email>/apikey", methods=["POST"])
def regenerate_apikey(email: str) -> tuple[Any, int]:
    try:
        verify_jwt_in_request()
        token_email = get_jwt_identity().lower()
    except Exception:
        return (
            jsonify(
                {"success": False, "msg": "Token no proporcionado o inválido. Por favor inicia sesión nuevamente."}
            ),
            401,
        )

    email = email.strip().lower()

    if token_email != email:
        return jsonify({"success": False, "msg": f"No tienes permiso para gestionar el API Key de otro usuario."}), 403
    try:
        data = request.get_json(silent=True) or {}
        expires = data.get("expires")

        result = user_service.regenerate_apikey(email.lower(), expires)
        return jsonify(result), 200

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 400

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@user_crud_router.route("/users/<email>/apikey", methods=["PATCH"])
def update_apikey_expiration(email: str) -> tuple[Any, int]:
    try:
        verify_jwt_in_request()
        token_email = get_jwt_identity().lower()
    except Exception:
        return (
            jsonify(
                {"success": False, "msg": "Token no proporcionado o inválido. Por favor inicia sesión nuevamente."}
            ),
            401,
        )

    email = email.strip().lower()

    if token_email != email:
        return jsonify({"success": False, "msg": "No tienes permiso para modificar el API Key de otro usuario."}), 403

    try:
        data = request.get_json(silent=True) or {}
        expires = data.get("expires")

        result = user_service.update_apikey_expiration(email, expires)
        return jsonify(result), 200

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 400
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500


@user_crud_router.route("/users/<email>/apikey", methods=["DELETE"])
def delete_apikey(email: str) -> tuple[Any, int]:
    try:
        verify_jwt_in_request()
        token_email = get_jwt_identity().lower()
    except Exception:
        return (
            jsonify(
                {"success": False, "msg": "Token no proporcionado o inválido. Por favor inicia sesión nuevamente."}
            ),
            401,
        )

    email = email.strip().lower()

    if token_email != email:
        return jsonify({"success": False, "msg": "No tienes permiso para eliminar el API Key de otro usuario."}), 403

    try:
        result = user_service.delete_apikey(email)
        return jsonify(result), 200

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 404
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500
