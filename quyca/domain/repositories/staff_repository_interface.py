from abc import ABC, abstractmethod


class IStaffRepository(ABC):
    """
    Contract to validate user tokens against persistence.
    """

    @abstractmethod
    def is_token_valid(self, email: str, token: str) -> bool:
        pass
