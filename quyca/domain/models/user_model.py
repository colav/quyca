from pydantic import BaseModel
from typing import Optional

"""
User entity used for authentication and account management.
"""


class User(BaseModel):
    id: str
    email: str
    password: Optional[str] = None
    institution: str
    rol: str
    token: Optional[str] = None
    is_active: bool = True
    apikey: Optional[dict] = None
