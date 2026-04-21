from typing import Protocol, Any


class ITokenService(Protocol):
    """Defines token creation and decoding operations."""

    def create_access_token(self, subject: str, claims: dict[str, Any]) -> str:
        """Creates an access token for the given subject."""
        ...

    def decode(self, token: str) -> dict[str, Any]:
        """Decodes a token and returns its claims."""
        ...
