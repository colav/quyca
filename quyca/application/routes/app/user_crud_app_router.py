from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from application.usecases.user_crud import UserCrudUseCase
from domain.exceptions.not_entity_exception import NotEntityException

"""
HTTP routes for admin user management (JWT-protected).
"""

user_crud_app_router = Blueprint("user_crud_app_router", __name__)
usecase = UserCrudUseCase()
def check_admin_permission():
    """Validates JWT exists and role is admin."""
    try:
        verify_jwt_in_request()
    except Exception:
        return {"success": False, "msg": "Token no proporcionado o inválido. Por favor, inicia sesión nuevamente."}, 401

    claims = get_jwt()
    user_rol = claims.get("rol")

    if user_rol.lower() != "admin":
        return {"success": False, "msg": "Permiso denegado: No pueden realizar esta acción."}, 403

    return None, None

@user_crud_app_router.route("/users/<email>", methods=["POST"])
def create_user(email):
    """Creates a user (admin-only)."""
    error_response, status = check_admin_permission()
    if error_response:
        return jsonify(error_response), status

    try:
        data = request.get_json()
        email = email.strip().lower()
        institution = data.get("institution")
        ror_id = data.get("ror_id")
        rol = data.get("rol")

        result = usecase.create_user(email, institution, ror_id, rol, data)
        
        if not result.get("success") and "ya existe" in result.get("msg", "").lower():
            return jsonify(result), 409
        
        return jsonify(result), 201
    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500
    
@user_crud_app_router.route("/users", methods=["GET"])
def list_users():
    """Lists users (admin-only, excludes admins)."""
    error_response, status = check_admin_permission()
    if error_response:
        return jsonify(error_response), status

    try:
        result = usecase.get_all_users()
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500

@user_crud_app_router.route("/users/<email>", methods=["DELETE"])
def deactivate_user(email):
    error_response, status = check_admin_permission()
    if error_response:
        return jsonify(error_response), status

    try:
        email = email.strip().lower()
        result = usecase.deactivate_user(email)
        return jsonify(result), 200

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500

@user_crud_app_router.route("/users/<email>/restore", methods=["PATCH"])
def activate_user(email):
    error_response, status = check_admin_permission()
    if error_response:
        return jsonify(error_response), status

    try:
        email = email.strip().lower()
        result = usecase.activate_user(email)
        return jsonify(result), 200

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500

@user_crud_app_router.route("/users/<email>", methods=["PATCH"])
def update_password(email):
    """Resets password and emails credentials (admin-only)."""
    error_response, status = check_admin_permission()
    if error_response:
        return jsonify(error_response), status

    try:
        email = email.strip().lower()

        result = usecase.update_password(email)
        return jsonify(result), 200
    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500
    
@user_crud_app_router.route("/users/<email>", methods=["PUT"])
def edit_user(email):
    """Edits email and/or role (admin-only) with admin-safety rules."""
    error_response, status = check_admin_permission()
    if error_response: 
        return jsonify(error_response), status
    
    try:
        old_email = email.strip().lower()
        data = request.get_json(force=True) or {}
        new_email = (data.get("email") or "").strip().lower()
        new_rol = (data.get("rol") or "").strip().lower()
        
        if not new_email and not new_rol:
            return jsonify({"success": False, "msg": "Debes enviar al menos email o rol."}), 400
        
        result = usecase.update_user_info(
            old_email,
            new_email or old_email,
            new_rol or "",
            data
        )
        if not result.get("success") and "rol 'admin'" in result.get("msg", "").lower():
            return jsonify(result), 403
        return jsonify(result), (200 if result.get("success") else 400)

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500