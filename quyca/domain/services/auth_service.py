from flask_jwt_extended import create_access_token, decode_token
from domain.repositories.user_repository_interface import IUserRepository
from domain.exceptions.not_entity_exception import NotEntityException
from domain.parsers.user_parser import user_ror_id_and_institution

"""
verifies user credentials using the repository, generates a JWT access token with the 
users rolID, stores the token in the database, and returns authentication details. If 
credentials are invalid
"""


def authenticate_user(email: str, password: str, repo: IUserRepository) -> dict:
    user = repo.get_by_email_and_pass(email, password)
    
    if not getattr(user, "is_active", True):
        raise NotEntityException("El usuario está desactivada. Contacte al administrador del sistema.")

    parse_user = user_ror_id_and_institution(user)

    additional_claims = {
        "ror_id": parse_user["ror_id"],
        "institution": parse_user["institution"],
        "rol": parse_user["rol"],
    }

    token = create_access_token(identity=user.email, additional_claims=additional_claims)

    repo.update_token(user.email, token)

    return {"success": True, **parse_user, "access_token": token}


"""
invalidates a given JWT token by decoding it to find the users email, removing the token
from the database, and returning a success message. 
If the token is invalid or expired
"""


def logout_user(token: str, repo: IUserRepository) -> dict:
    try:
        decode = decode_token(token)
        email = decode.get("sub")
        if not email:
            return {"success": False, "msg": "Problema en el token"}
        removed = repo.remove_token(email, token)
        if not removed:
            return {"success": False, "msg": "Token inválido o ya caducado"}
        return {"success": True, "msg": "Sesión cerrada correctamente"}
    except Exception as e:
        return {"success": False, "msg": str(e)}
