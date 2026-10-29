class ForbiddenException(Exception):
    """The session is valid but may not do this (not admin, another user's account, deactivated). HTTP 403."""
