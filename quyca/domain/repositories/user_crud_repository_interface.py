from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from domain.models.user_model import User


class IUserCrudRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> None:
        """Creates a new user document."""

    @abstractmethod
    def get_all(self) -> List[User]:
        """Returns all user entities."""

    @abstractmethod
    def update_password(self, email: str, new_password_hash: str) -> User:
        """Updates a user's password and returns updated user."""

    @abstractmethod
    def update_user_info(self, old_email: str, new_email: str, new_rol: str) -> Optional[User]:
        """Updates email/role and returns updated user."""

    @abstractmethod
    def find_by_ror_id(self, ror_id: str) -> Optional[User]:
        """Returns user by ROR ID if exists."""

    @abstractmethod
    def deactivate(self, email: str) -> None:
        """Marks user as inactive."""

    @abstractmethod
    def activate(self, email: str) -> None:
        """Marks user as active."""

    @abstractmethod
    def regenerate_apikey(self, email: str, new_apikey: Dict[str, Any]) -> None:
        """Creates or replaces user's API key."""

    @abstractmethod
    def update_apikey_expiration(self, email: str, new_expiration: int | None) -> None:
        """Updates expiration timestamp of API key."""

    @abstractmethod
    def delete_apikey(self, email: str) -> None:
        """Deletes user's API key."""
