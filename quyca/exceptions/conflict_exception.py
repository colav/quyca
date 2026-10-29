class ConflictException(Exception):
    """The change collides with existing data (the email or institution already has a user). HTTP 409."""
