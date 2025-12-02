import hashlib
from domain.models.user_model import User
from infrastructure.mongo import impactu_database
from domain.exceptions.not_entity_exception import NotEntityException
from domain.repositories.user_repository_interface import IUserRepository

"""
MongoDB repository for login + token management.
"""


class UserRepositoryMongo(IUserRepository):
    def __init__(self) -> None:
        """Initializes Mongo collection handle."""
        self.collection = impactu_database["users"]

    def get_by_email_and_pass(self, email: str, password: str) -> User:
        """Validates credentials and returns a user or raises error."""
        email = email.strip().lower()
        password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()

        user_data = self.collection.find_one(
            {"email": email.strip().lower(), "password": password_hash}, {"password": 0}
        )
        if not user_data:
            raise NotEntityException(f"Usuario con correo {email} no encontrado o contraseño no conciden")
        return User(
            id=str(user_data["_id"]),
            email=user_data["email"],
            institution=user_data["institution"],
            rol=user_data["rol"],
            token=user_data.get("token"),
            is_active=user_data.get("is_active", True),
            apikey=user_data.get("apikey"),
        )

    def update_token(self, email: str, token: str) -> None:
        """Stores or refreshes the latest token for a user."""
        self.collection.update_one({"email": email.strip().lower()}, {"$set": {"token": token}})

    def remove_token(self, email: str, token: str) -> bool:
        """Clears token if it matches the stored one."""
        user = self.collection.find_one({"email": email.strip().lower()}, {"password": 0, "token": 0})
        if user and user.get("token") == token:
            self.collection.update_one({"email": email.strip().lower()}, {"$set": {"token": ""}})
            return True
        return False

    def is_token_valid(self, email: str, token: str) -> bool:
        """Checks if the given token is currently valid for the user."""
        user = self.collection.find_one({"email": email.strip().lower()}, {"password": 0})
        return user is not None and user.get("token") == token
