from abc import ABC, abstractmethod
from domain.models.user_model import User


class IUserRepository(ABC):
    """Contract that every User repository must implement."""

    @abstractmethod
    def get_by_email_and_pass(self, email: str, password: str) -> User:
        pass

    @abstractmethod
    def update_token(self, email: str, token: str) -> None:
        pass

    @abstractmethod
    def remove_token(self, email: str, token: str) -> bool:
        pass
