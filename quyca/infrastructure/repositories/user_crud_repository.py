from typing import List, Optional, Dict, Any
from quyca.domain.models.user_model import User
from quyca.infrastructure.mongo import impactu_database
from quyca.domain.repositories.user_crud_repository_interface import IUserCrudRepository
from quyca.domain.exceptions.not_entity_exception import NotEntityException


class UserCrudRepository(IUserCrudRepository):
    """
    MongoDB repository for admin CRUD on users.
    """

    def __init__(self) -> None:
        self.collection = impactu_database["users"]

    def create(self, user: User) -> None:
        """Inserts a new user if the email is not already registered."""
        email = user.email.strip().lower()
        existing = self.collection.find_one({"email": email}, {"password": 0})
        if existing:
            raise NotEntityException(f"El usuario con correo {email} ya existe.")

        self.collection.insert_one(
            {
                "_id": user.id,
                "email": user.email,
                "password": user.password,
                "institution": user.institution,
                "role": user.role,
                "is_active": user.is_active,
                "apikey": user.apikey,
            }
        )

    def get_all(self) -> List[User]:
        """Returns all users without exposing password hashes."""
        users_cursor = self.collection.find({}, {"password": 0})
        users = list(users_cursor)

        return [
            User(
                id=str(u["_id"]),
                email=u["email"],
                password=None,
                institution=u["institution"],
                role=u["role"],
                is_active=u.get("is_active", True),
                apikey=u.get("apikey"),
            )
            for u in users
        ]

    def update_password(self, email: str, new_password_hash: str) -> User:
        """Updates the password hash for a user and returns the updated user."""
        result = self.collection.update_one({"email": email.lower()}, {"$set": {"password": new_password_hash}})

        if result.matched_count == 0:
            raise NotEntityException(f"Usuario con correo {email} no encontrado")

        updated = self.collection.find_one({"email": email.lower()}, {"password": 0})
        if not updated:
            raise NotEntityException(f"Usuario con correo {email} no encontrado")
        return User(
            id=str(updated["_id"]),
            email=updated["email"],
            password=None,
            institution=updated["institution"],
            role=updated["role"],
            is_active=updated.get("is_active", True),
            apikey=updated.get("apikey"),
        )

    def deactivate(self, email: str) -> None:
        """Sets is_active=False for the given email."""
        email = email.lower()
        user = self.collection.find_one({"email": email})
        if not user:
            raise NotEntityException(f"Usuario con correo {email} no encontrado")

        self.collection.update_one({"email": email}, {"$set": {"is_active": False}})

    def activate(self, email: str) -> None:
        """Sets is_active=True for the given email."""
        email = email.lower()
        user = self.collection.find_one({"email": email})
        if not user:
            raise NotEntityException(f"Usuario con correo {email} no encontrado")

        self.collection.update_one({"email": email}, {"$set": {"is_active": True}})

    def update_user_info(self, old_email: str, new_email: str, new_role: str) -> Optional[User]:
        """Updates email and/or role and returns the updated user (or None if missing)."""
        doc = self.collection.find_one({"email": old_email}, {"password": 0})
        if not doc:
            return None

        update = {}

        if new_email and new_email != old_email:
            if self.collection.find_one({"email": new_email}):
                raise NotEntityException(f"Ya existe un usuario con el correo {new_email}")
            update["email"] = new_email

        if new_role:
            update["role"] = new_role

        if not update:
            return User(
                id=str(doc["_id"]),
                email=doc["email"],
                password=None,
                institution=doc["institution"],
                role=doc["role"],
                is_active=doc.get("is_active", True),
                apikey=doc.get("apikey"),
            )

        self.collection.update_one({"email": old_email}, {"$set": update})

        updated = self.collection.find_one({"email": update.get("email", old_email)}, {"password": 0})
        if not updated:
            return None

        return User(
            id=str(updated["_id"]),
            email=updated["email"],
            password=None,
            institution=updated["institution"],
            role=updated["role"],
            is_active=updated.get("is_active", True),
            apikey=updated.get("apikey"),
        )

    def find_by_ror_id(self, ror_id: str) -> Optional[User]:
        """Finds a user by their ROR id (stored as _id)."""
        doc = self.collection.find_one({"_id": ror_id}, {"password": 0})
        if not doc:
            return None

        return User(
            id=str(doc["_id"]),
            email=doc["email"],
            password=None,
            institution=doc["institution"],
            role=doc["role"],
            is_active=doc.get("is_active", True),
            apikey=doc.get("apikey"),
        )

    def regenerate_apikey(self, email: str, new_apikey: Dict[str, Any]) -> None:
        """Replaces the user's API key object."""
        result = self.collection.update_one({"email": email.lower()}, {"$set": {"apikey": new_apikey}})
        if result.matched_count == 0:
            raise NotEntityException(f"Usuario {email} no encontrado")

    def update_apikey_expiration(self, email: str, new_expiration: int | None) -> None:
        """Updates only the apikey.expires field."""
        result = self.collection.update_one({"email": email.lower()}, {"$set": {"apikey.expires": new_expiration}})
        if result.matched_count == 0:
            raise NotEntityException(f"Usuario {email} no encontrado")

    def delete_apikey(self, email: str) -> None:
        """Removes the API key by setting apikey=None."""
        result = self.collection.update_one({"email": email.lower()}, {"$set": {"apikey": None}})
        if result.matched_count == 0:
            raise NotEntityException(f"Usuario {email} no encontrado")
