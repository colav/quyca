from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.user_model import User

"""
Interface for user CRUD repository (admin operations).
"""

class IUserCrudRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        """Creates a new user document."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[User]:
        """Lists all users (usually hiding sensitive fields)."""
        pass
    
    @abstractmethod
    def update_password(self, email: str, new_password_hash: str) -> Optional[User]:
        """Updates the user's password hash."""
        pass
    
    @abstractmethod
    def update_user_info(self, old_email: str, new_email: str, new_rol: str) -> dict:
        """Updates email and/or role of a user (admin use)."""
        pass
    
    @abstractmethod
    def find_by_ror_id(self, ror_id: str) -> dict:
        """Finds a user by ROR id (one account per institution rule)."""
        pass
    
    @abstractmethod
    def deactivate(self, email: str) -> User:
        pass
    
    @abstractmethod
    def activate(self, email: str) -> User:
        pass
    
    @abstractmethod
    def regenerate_apikey(self, email: str, new_apikey: dict):
        pass

    @abstractmethod
    def update_apikey_expiration(self, email: str, new_expiration: int | None):
        pass

    @abstractmethod
    def delete_apikey(self, email: str):
        pass