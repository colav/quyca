from quyca.domain.models.user_model import User
from quyca.infrastructure.mongo import impactu_database
from quyca.infrastructure.security.password_hasher import verify_password
from quyca.domain.exceptions.not_entity_exception import NotEntityException
from quyca.domain.repositories.user_repository_interface import IUserRepository

"""
MongoDB repository for login + token management.
"""


class UserRepositoryMongo(IUserRepository):
    """MongoDB repository for authenticating users by email/password."""

    def __init__(self) -> None:
        self.collection = impactu_database["users"]

    def get_by_email_and_pass(self, email: str, password: str) -> User:
        """Validates credentials and returns the user data."""
        email = email.strip().lower()

        user_data = self.collection.find_one(
            {"email": email.strip().lower()},
            {"password": 1, "email": 1, "institution": 1, "role": 1, "is_active": 1, "apikey": 1},
        )

        if not user_data:
            raise NotEntityException(f"Usuario con correo {email} no encontrado o contraseña no conciden")

        stored_hash = user_data.get("password")
        try:
            if not stored_hash or not verify_password(password, stored_hash):
                raise NotEntityException(f"Usuario con correo {email} no encontrado o contraseña no conciden")
        except Exception:
            raise NotEntityException(f"Usuario con correo {email} no encontrado o contraseña no conciden")

        return User(
            id=str(user_data["_id"]),
            email=user_data["email"],
            institution=user_data["institution"],
            role=user_data["role"],
            is_active=user_data.get("is_active", True),
            apikey=user_data.get("apikey"),
        )
