from typing import Any, Optional
from domain.repositories.staff_repository_interface import IStaffRepository
from pymongo.database import Database


class StaffRepository(IStaffRepository):
    def __init__(self, db: Database) -> None:
        self.collection = db["users"]

    """Checks if a users token is valid by comparing with the database"""

    def is_token_valid(self, email: str, token: str) -> bool:
        user: Optional[dict[str, Any]] = self.collection.find_one({"email": email.strip().lower()})
        if user is None:
            return False
        return user.get("token") == token
