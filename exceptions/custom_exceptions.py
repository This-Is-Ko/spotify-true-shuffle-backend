class SessionIdNotFound(Exception):
    """
    session_id doesn't exist in database
    """
    pass


class SessionIdNone(Exception):
    """
    session_id value is None
    """
    pass


class SessionExpired(Exception):
    """
    session has expired
    """
    pass


class AccessTokenInvalid(Exception):
    """
    access token is invalid
    """
    pass
