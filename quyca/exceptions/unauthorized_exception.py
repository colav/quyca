class UnauthorizedException(Exception):
    """There is no valid session (missing or expired token, wrong credentials). Answered with HTTP 401."""
