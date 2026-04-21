from typing import Any
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from quyca.domain.auth.auth_ports import IJwtVerifier


class FlaskJwtVerifier(IJwtVerifier):
    """Verifies JWT tokens extracted from cookies."""

    def verify_from_cookies(self) -> dict[str, Any] | None:
        """Validates the JWT from cookies and returns its claims."""
        try:
            verify_jwt_in_request(locations=["cookies"])
            return dict(get_jwt())
        except Exception:
            return None
