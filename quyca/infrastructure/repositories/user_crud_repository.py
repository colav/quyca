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
        self.collection.insert_one(user.model_dump())
        return user
    
    def get_all(self) -> List[User]:
        """Returns all users without sensitive fields."""
        users_cursor = self.collection.find({}, {"password": 0, "token": 0})
        users = list(users_cursor)
        
        return [User(**u) for u in users]

    def update_password(self, email: str, new_password_hash: str) -> Optional[User]:
        """Updates password hash for a given user."""
        result = self.collection.update_one(
            {"email": email.strip().lower()},
            {"$set": {"password": new_password_hash}}
        )
        
        if result.matched_count == 0:
            raise NotEntityException(f"Usuario con correo {email} no encontrado")
        
        updated = self.collection.find_one({"email": email.strip().lower()}, {"password": 0, "token": 0})
        return User(**updated) if updated else None
        
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
        return User(**updated) if updated else None
    
    def activate(self, email: str) -> User:
        email = email.strip().lower()
        user = self.collection.find_one({"email": email}, {"password": 0, "token": 0})
        if not user:
            raise NotEntityException(f"Usuario con correo {email} no encontrado")
        
        self.collection.update_one({"email": email}, {"$set": {"is_active": True}})
        updated = self.collection.find_one({"email": email}, {"password": 0, "token": 0})
        return User(**updated)
    
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
            return User(**doc)

        self.collection.update_one({"email": old_email}, {"$set": update})
        updated = self.collection.find_one({"email": update.get("email", old_email)}, {"password": 0, "token": 0})
        return User(**updated) if updated else None
    
    def find_by_ror_id(self, ror_id: str) -> Optional[User]:
        """Finds the first user for a given ROR id."""
        doc = self.collection.find_one({"ror_id": ror_id}, {"password": 0, "token": 0})
        return User(**doc) if doc else None