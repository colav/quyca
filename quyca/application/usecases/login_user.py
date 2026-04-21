from dataclasses import dataclass
from typing import Any, Optional

from quyca.application.ports.token_service import ITokenService
from quyca.domain.parsers.user_parser import user_ror_id_and_institution
from quyca.domain.exceptions.not_entity_exception import NotEntityException
from quyca.domain.repositories.user_repository_interface import IUserRepository


@dataclass
class LoginResult:
    success: bool
    access_token: Optional[str] = None
    rorID: Optional[Any] = None
    institution: Optional[Any] = None
    user_id: Optional[Any] = None
    message: Optional[str] = None


class LoginUserUseCase:
    """Use case responsible for authenticating users."""

    def __init__(self, user_repo: IUserRepository, token_service: ITokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    def execute(self, email: str, password: str) -> dict:
        """Validates credentials and returns an access token if successful."""
        email = (email or "").strip()
        password = password or ""

        if not email or not password:
            return {"success": False, "msg": "correo y contraseña requeridos"}

        user = self.user_repo.get_by_email_and_pass(email, password)

        if not user:
            return {"success": False, "msg": "Credenciales inválidas"}

        if not getattr(user, "is_active", True):
            raise NotEntityException("El usuario está desactivado. Contacte al administrador del sistema")

        parse_user = user_ror_id_and_institution(user)

        claims: dict[str, Any] = {
            "_id": parse_user["_id"],
            "institution": parse_user["institution"],
            "role": parse_user["role"],
        }

        token = self.token_service.create_access_token(subject=user.email, claims=claims)

        return {
            "success": True,
            **parse_user,
            "access_token": token,
        }
