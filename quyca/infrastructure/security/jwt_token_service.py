from flask_jwt_extended import create_access_token, decode_token


class JwtTokenService:
    """JWT token generation and decoding adapter."""

    def create_access_token(self, subject: str, claims: dict) -> str:
        """Create JWT access token."""
        return create_access_token(identity=subject, additional_claims=claims)

    def decode(self, token: str) -> dict:
        """Decode JWT token payload."""
        return decode_token(token)
