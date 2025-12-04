from abc import ABC, abstractmethod
from domain.models.user_model import User


class IUserRepository(ABC):
    """
    Interface for auth repository (login, token operations).
    """

    @abstractmethod
    def get_by_email_and_pass(self, email: str, password: str) -> User:
        """Fetches a user by email and password hash for login."""

    @abstractmethod
    def update_token(self, email: str, token: str) -> None:
        """Persists the latest JWT token for the user."""

    @abstractmethod
    def remove_token(self, email: str, token: str) -> bool:
        """Invalidates a stored JWT token for the user."""
