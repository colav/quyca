from domain.models.user_model import User
from infrastructure.mongo import impactu_database
from domain.exceptions.not_entity_exception import NotEntityException
from domain.repositories.user_repository_interface import IUserRepository


class UserRepositoryMongo(IUserRepository):
    def __init__(self) -> None:
        self.collection = impactu_database["users"]

    """
    The get_by_email_and_pass method retrieves a user by email and password,
    returning a User object or raising NotEntityException if not found.
    """

    def get_by_email_and_pass(self, email: str, password: str) -> User:
        user_data = self.collection.find_one({"email": email.strip().lower(), "password": password})
        if not user_data:
            raise NotEntityException(f"Usuario con correo {email} no encontrado o contraseño no conciden")
        return User(
            email=user_data["email"],
            password=user_data["password"],
            institution=user_data["institution"],
            ror_id=user_data["ror_id"],
            rol=user_data["rol"],
            token=user_data["token"],
        )

    """
    updates to the latest valid token
    """

    def update_token(self, email: str, token: str) -> None:
        self.collection.update_one({"email": email.strip().lower()}, {"$set": {"token": token}})

    """Delete token"""

    def remove_token(self, email: str, token: str) -> bool:
        user = self.collection.find_one({"email": email.strip().lower()})
        if user and user.get("token") == token:
            self.collection.update_one({"email": email.strip().lower()}, {"$set": {"token": ""}})
            return True
        return False

    """valid token"""

    def is_token_valid(self, email: str, token: str) -> bool:
        user = self.collection.find_one({"email": email.strip().lower()})
        return user is not None and user.get("token") == token
