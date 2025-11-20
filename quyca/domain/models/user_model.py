from pydantic import BaseModel
from typing import Optional

"""
User entity used for authentication and account management.
"""


class User(BaseModel):
    email: str
    password: Optional[str] = None
    institution: str
    ror_id: str | None = None
    rol: str
    token: Optional[str] = None
    is_active: bool = True
