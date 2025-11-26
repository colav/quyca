from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
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


"""
@api {post} /app/admin/users/:email Create user (admin only)
@apiName CreateUser
@apiGroup Users
@apiVersion 1.0.0

@apiDescription
Creates a new user in the platform. Only users with role admin can perform this action.

@apiHeader {String} Authorization JWT token in format "Bearer &lt;token&gt;"

@apiParam (Path) {String} email User email passed in URL

@apiBody {String} institution Institution name
@apiBody {String} ror_id Institution ROR identifier
@apiBody {String} rol User role in the application

@apiSuccess (201) {Boolean} success true
@apiSuccess (201) {String} msg Success message

@apiError (400) {Boolean} success false
@apiError (400) {String} msg Validation or payload error

@apiError (401) {Boolean} success false
@apiError (401) {String} msg Token missing or invalid

@apiError (409) {Boolean} success false
@apiError (409) {String} msg User already exists for the institution

@apiExample {json} Request Body Example
{
    "institution": "Universidad de Antioquia",
    "ror_id": "059yx9a68",
    "rol": "staff"
}
"""


@user_crud_app_router.route("/admin/users/<email>", methods=["POST"])
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


"""
@api {get} /app/users List users (non-admin)
@apiName ListUsers
@apiGroup Users
@apiVersion 1.0.0

@apiDescription
Returns a list of all users except those with admin role. Requires admin token.

@apiHeader {String} Authorization JWT token "Bearer &lt;token&gt;"

@apiSuccess (200) {Boolean} success true
@apiSuccess (200) {Object[]} data List of users
@apiSuccess (200) {String} data.email User email
@apiSuccess (200) {String} data.institucion Institution name
@apiSuccess (200) {String} data.id User identifier
@apiSuccess (200) {String} data.rol User role
@apiSuccess (200) {Boolean} data.is_active Active status

@apiError (401) {Boolean} success false
@apiError (401) {String} msg Token missing or invalid
"""


@user_crud_app_router.route("/admin/users", methods=["GET"])
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


"""
@api {delete} /app/admin/users/:email Deactivate user
@apiName DeactivateUser
@apiGroup Users
@apiVersion 1.0.0

@apiDescription
Deactivates a user account by setting is_active to false.

@apiHeader {String} Authorization JWT token "Bearer &lt;token&gt;"

@apiParam (Path) {String} email User email

@apiSuccess (200) {Boolean} success true
@apiSuccess (200) {String} msg Deactivation message

@apiError (404) {Boolean} success false
@apiError (404) {String} msg User not found

@apiError (401) {Boolean} success false
@apiError (401) {String} msg Token invalid or missing
"""


@user_crud_app_router.route("/admin/users/<email>", methods=["DELETE"])
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


"""
@api {patch} /app/admin/users/:email/restore Activate user
@apiName ActivateUser
@apiGroup Users
@apiVersion 1.0.0

@apiDescription
Reactivates a deactivated user by setting is_active to true.

@apiHeader {String} Authorization JWT token "Bearer &lt;token&gt;"

@apiParam (Path) {String} email User email

@apiSuccess (200) {Boolean} success true
@apiSuccess (200) {String} msg Activation message

@apiError (404) {Boolean} success false
@apiError (404) {String} msg User not found
"""


@user_crud_app_router.route("/admin/users/<email>/restore", methods=["PATCH"])
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


"""
@api {patch} /app/admin/users/:email Reset user password
@apiName ResetPassword
@apiGroup Users
@apiVersion 1.0.0

@apiDescription
Resets the user password and sends the new credentials via email.

@apiHeader {String} Authorization JWT token "Bearer &lt;token&gt;"

@apiParam (Path) {String} email User email

@apiSuccess (200) {Boolean} success true
@apiSuccess (200) {String} msg Password updated

@apiError (400) {Boolean} success false
@apiError (400) {String} msg User not found or account disabled
"""


@user_crud_app_router.route("/admin/users/<email>", methods=["PATCH"])
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


"""
@api {put} /app/admin/users/:email Edit user email or role
@apiName EditUser
@apiGroup Users
@apiVersion 1.0.0

@apiDescription
Edits the email and/or role of a user. It is not allowed to assign admin role or edit admin accounts.

@apiHeader {String} Authorization JWT token "Bearer &lt;token&gt;"

@apiParam (Path) {String} email Current user email

@apiBody {String} [email] New email
@apiBody {String} [rol] New role

@apiSuccess (200) {Boolean} success true
@apiSuccess (200) {String} msg Update message

@apiError (400) {Boolean} success false
@apiError (400) {String} msg No changes detected or invalid payload

@apiError (403) {Boolean} success false
@apiError (403) {String} msg Not allowed to assign admin role

@apiError (404) {Boolean} success false
@apiError (404) {String} msg User not found
"""


@user_crud_app_router.route("/admin/users/<email>", methods=["PUT"])
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

        result = usecase.update_user_info(old_email, new_email or old_email, new_rol or "", data)
        if not result.get("success") and "rol 'admin'" in result.get("msg", "").lower():
            return jsonify(result), 403
        return jsonify(result), (200 if result.get("success") else 400)

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


"""
@api {post} /app/users/:email/apikey Generate or regenerate API Key
@apiName RegenerateApiKey
@apiGroup ApiKey
@apiVersion 1.0.0

@apiDescription
Generates a new API Key for the authenticated user. If an API Key exists, it is replaced.

@apiHeader {String} Authorization JWT token "Bearer &lt;token&gt;"

@apiParam (Path) {String} email User email (must match token identity)

@apiBody {Number} [expires] Expiration timestamp in seconds (optional, must be future and at least 1 day away)

@apiSuccess (200) {Boolean} success true
@apiSuccess (200) {Object} apikey API Key object
@apiSuccess (200) {String} apikey.id Key identifier
@apiSuccess (200) {Number} [apikey.expires] Expiration timestamp

@apiError (401) {Boolean} success false
@apiError (401) {String} msg Token missing or invalid

@apiError (403) {Boolean} success false
@apiError (403) {String} msg Not allowed to manage another user's API Key

@apiError (400) {Boolean} success false
@apiError (400) {String} msg Invalid expiration value
"""


@user_crud_app_router.route("/users/<email>/apikey", methods=["POST"])
def regenerate_apikey(email):
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

        result = usecase.create_or_regenerate_apikey(email.lower(), expires)
        return jsonify(result), 200

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 400

    except Exception as e:
        return jsonify({"success": False, "msg": "Error interno del servidor", "detail": str(e)}), 500


"""
@api {patch} /app/users/:email/apikey Update API Key expiration
@apiName UpdateApiKeyExpiration
@apiGroup ApiKey
@apiVersion 1.0.0

@apiDescription
Updates the expiration timestamp of the user's existing API Key.

@apiHeader {String} Authorization JWT token "Bearer &lt;token&gt;"

@apiParam (Path) {String} email User email (must match token identity)

@apiBody {Number} expires New expiration timestamp (future, at least 1 day away)

@apiSuccess (200) {Boolean} success true
@apiSuccess (200) {String} msg Expiration updated successfully

@apiError (401) {Boolean} success false
@apiError (401) {String} msg Token missing or invalid

@apiError (403) {Boolean} success false
@apiError (403) {String} msg Not allowed to modify another user's API Key

@apiError (400) {Boolean} success false
@apiError (400) {String} msg Invalid expiration
"""


@user_crud_app_router.route("/users/<email>/apikey", methods=["PATCH"])
def update_apikey_expiration(email):
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

        result = usecase.update_apikey_expiration(email, expires)
        return jsonify(result), 200

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


"""
@api {delete} /app/users/:email/apikey Delete API Key
@apiName DeleteApiKey
@apiGroup ApiKey
@apiVersion 1.0.0

@apiDescription
Deletes the API Key associated with the authenticated user.

@apiHeader {String} Authorization JWT token "Bearer &lt;token&gt;"

@apiParam (Path) {String} email User email (must match token identity)

@apiSuccess (200) {Boolean} success true
@apiSuccess (200) {String} msg API Key deleted successfully

@apiError (401) {Boolean} success false
@apiError (401) {String} msg Token missing or invalid

@apiError (403) {Boolean} success false
@apiError (403) {String} msg Not allowed to delete another user's API Key

@apiError (404) {Boolean} success false
@apiError (404) {String} msg User not found
"""


@user_crud_app_router.route("/users/<email>/apikey", methods=["DELETE"])
def delete_apikey(email):
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
        result = usecase.delete_apikey(email)
        return jsonify(result), 200

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500
