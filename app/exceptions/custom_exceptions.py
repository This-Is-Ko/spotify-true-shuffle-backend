class SessionIdNotFound(Exception):
    """
    Session_id doesn't exist in database
    """
    pass


class SessionIdNone(Exception):
    """
    Session_id value is None
    """
    pass


class SessionExpired(Exception):
    """
    Session has expired
    """
    pass


class AccessTokenInvalid(Exception):
    """
    Access token is invalid
    """
    pass


class SpotifyAuthInvalid(Exception):
    """
    Spotify auth info is invalid
    """
    pass

class InvalidUser(Exception):
    """
    Invalid user exception
    """
    pass

class GetPlaylistsException(Exception):
    """
    Get playlists exception
    """
    pass
