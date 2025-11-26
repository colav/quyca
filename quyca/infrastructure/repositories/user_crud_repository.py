from typing import List, Optional
from domain.models.user_model import User
from infrastructure.mongo import impactu_database
from domain.repositories.user_crud_repository_interface import IUserCrudRepository
from domain.exceptions.not_entity_exception import NotEntityException

class UserCrudRepository(IUserCrudRepository):
    """
    MongoDB repository for admin CRUD on users.
    """
    def __init__(self):
        """Initializes Mongo collection handle."""
        self.collection = impactu_database["users"]

    def create(self, user: User) -> User:
        """Creates a new user if email is unique."""
        email = user.email.strip().lower()
        existing = self.collection.find_one({"email": email}, {"password": 0, "token": 0})
        if existing:
            raise NotEntityException(f"El usuario con correo {email} ya existe.")
        self.collection.insert_one({
            "_id": user.id,  
            "email": user.email,
            "password": user.password,
            "institution": user.institution,
            "rol": user.rol,
            "token": user.token,
            "is_active": user.is_active,
            "apikey": user.apikey
        })
        return user
    
    def get_all(self) -> List[User]:
        """Returns all users without sensitive fields."""
        users_cursor = self.collection.find({}, {"password": 0, "token": 0})
        users = list(users_cursor)
        
        return [
            User(
                id=str(u["_id"]),
                email=u["email"],
                password=None,
                institution=u["institution"],
                rol=u["rol"],
                token=u.get("token"),
                is_active=u.get("is_active", True),
                apikey=u.get("apikey")
            )
            for u in users
        ]

    def update_password(self, email: str, new_password_hash: str) -> Optional[User]:
        """Updates password hash for a given user."""
        result = self.collection.update_one(
            {"email": email.strip().lower()},
            {"$set": {"password": new_password_hash}}
        )
        
        if result.matched_count == 0:
            raise NotEntityException(f"Usuario con correo {email} no encontrado")
        
        updated = self.collection.find_one({"email": email.strip().lower()}, {"password": 0, "token": 0})
        return User(
            id=str(updated["_id"]),
            email=updated["email"],
            password=None,
            institution=updated["institution"],
            rol=updated["rol"],
            is_active=updated.get("is_active", True),
            token=updated.get("token"),
            apikey=updated.get("apikey")
        )
        
    def deactivate(self, email: str) -> User:
        """Toggles is_active for the user."""
        email = email.strip().lower()
        user = self.collection.find_one({"email": email}, {"password": 0, "token": 0})
        if not user:
            raise NotEntityException(f"Usuario con correo {email} no encontrado")
        
        self.collection.update_one(
            {"email": email},
            {"$set": {"is_active": False}}
        )
        
        updated = self.collection.find_one({"email": email}, {"password": 0, "token": 0})
        return User(
            id=str(updated["_id"]),
            email=updated["email"],
            password=None,
            institution=updated["institution"],
            rol=updated["rol"],
            token=updated.get("token"),
            is_active=updated.get("is_active", True),
            apikey=updated.get("apikey")
        ) if updated else None
    
    def activate(self, email: str) -> User:
        email = email.strip().lower()
        user = self.collection.find_one({"email": email}, {"password": 0, "token": 0})
        if not user:
            raise NotEntityException(f"Usuario con correo {email} no encontrado")
        
        self.collection.update_one({"email": email}, {"$set": {"is_active": True}})
        doc = self.collection.find_one({"email": email}, {"password": 0, "token": 0})
        return User(
            id=str(doc["_id"]),
            email=doc["email"],
            password=None,
            institution=doc["institution"],
            rol=doc["rol"],
            token=doc.get("token"),
            is_active=doc.get("is_active", True),
            apikey=doc.get("apikey")
        )
    
    def update_user_info(self, old_email: str, new_email: str, new_rol: str) -> Optional[User]:
        """Updates email and/or role, avoiding collisions on email."""
        doc = self.collection.find_one({"email": old_email}, {"password": 0, "token": 0})
        if not doc:
            return None

        update = {}
        if new_email and new_email != old_email:
            if self.collection.find_one({"email": new_email}, {"password": 0, "token": 0}):
                raise NotEntityException(f"Ya existe un usuario con el correo {new_email}")
            update["email"] = new_email

        if new_rol:
            update["rol"] = new_rol

        if not update:
            return User(
                id=str(doc["_id"]),
                email=doc["email"],
                password=None,
                institution=doc["institution"],
                rol=doc["rol"],
                is_active=doc.get("is_active", True),
                token=doc.get("token"),
                apikey=doc.get("apikey")
            )

        self.collection.update_one({"email": old_email}, {"$set": update})
        updated = self.collection.find_one({"email": update.get("email", old_email)}, {"password": 0, "token": 0})
        return User(
                id=str(updated["_id"]),
                email=updated["email"],
                password=None,
                institution=updated["institution"],
                rol=updated["rol"],
                is_active=updated.get("is_active", True),
                token=updated.get("token"),
                apikey=updated.get("apikey")
            )
    
    def find_by_ror_id(self, ror_id: str) -> Optional[User]:
        """Finds the first user for a given ROR id."""
        doc = self.collection.find_one({"_id": ror_id}, {"password": 0, "token": 0})
        if not doc:
            return None
        
        return User(
            id=str(doc["_id"]),
            email=doc["email"],
            password=None,
            institution=doc["institution"],
            rol=doc["rol"],
            token=doc.get("token"),
            is_active=doc.get("is_active", True),
            apikey=doc.get("apikey")
        )
    
    def regenerate_apikey(self, email: str, new_apikey: dict):
        result = self.collection.update_one(
            {"email": email.lower()},
            {"$set": {"apikey": new_apikey}}
        )
        if result.matched_count == 0:
            raise NotEntityException(f"Usuario {email} no encontrado")

    def update_apikey_expiration(self, email: str, new_expiration):
        result = self.collection.update_one(
            {"email": email.lower()},
            {"$set": {"apikey.expires": new_expiration}}
        )
        if result.matched_count == 0:
            raise NotEntityException(f"Usuario {email} no encontrado")

    def delete_apikey(self, email: str):
        result = self.collection.update_one(
            {"email": email.lower()},
            {"$set": {"apikey": None}}
        )
        if result.matched_count == 0:
            raise NotEntityException(f"Usuario {email} no encontrado")