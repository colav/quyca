from typing import Protocol, Any


class IJwtCookieReader(Protocol):
    def get_access_token(self) -> str | None:
        """Returns the access token stored in cookies."""
        ...


class IJwtVerifier(Protocol):
    def verify_from_cookies(self) -> dict[str, Any] | None:
        """Verifies the token from cookies and returns its claims."""
        ...
