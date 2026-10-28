from typing import Any

import flask_jwt_extended
from flask import current_app, request


def create_access_token(subject: str, claims: dict) -> str:
    """Create JWT access token."""
    return flask_jwt_extended.create_access_token(identity=subject, additional_claims=claims)


def get_access_token_cookie() -> str | None:
    """Returns the raw access token cookie of the current request, if any."""
    cookie_name = current_app.config.get("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")
    return request.cookies.get(cookie_name)


def verify_cookie_claims() -> dict[str, Any] | None:
    """Validates the JWT from cookies and returns its claims, or None when it is missing, expired or invalid."""
    try:
        flask_jwt_extended.verify_jwt_in_request(locations=["cookies"])
        return dict(flask_jwt_extended.get_jwt())
    except Exception:
        return None
