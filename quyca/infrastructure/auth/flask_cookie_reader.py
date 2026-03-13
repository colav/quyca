from flask import request, current_app
from quyca.domain.auth.auth_ports import IJwtCookieReader


class FlaskJwtCookieReader(IJwtCookieReader):
    """Reads the JWT access token from request cookies."""

    def get_access_token(self) -> str | None:
        """Retrieves the access token cookie value."""
        cookie_name = current_app.config.get("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")
        return request.cookies.get(cookie_name)
