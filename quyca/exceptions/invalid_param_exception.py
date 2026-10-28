class InvalidParamException(Exception):
    """A request parameter (query string or path) has an invalid value. Answered with HTTP 400."""
