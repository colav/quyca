from pydantic import BaseModel

"""
Auth user model used across services (JWT + persistence).
"""


class User(BaseModel):
    email: str
    password: str
    institution: str
    ror_id: str | None = None
    rol: str
    token: str
