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
