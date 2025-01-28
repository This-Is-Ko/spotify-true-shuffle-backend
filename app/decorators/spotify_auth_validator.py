from functools import wraps
from flask import current_app, request
from exceptions.custom_exceptions import SessionExpired, SessionIdNone, SessionIdNotFound
from utils.auth_utils import validate_session


def spotify_auth_validator(f):
    """
    Decorator for Flask endpoints to validate a user's Spotify session.
    If the session is valid, it injects the `spotify_auth` object into the decorated function.
    If the session is invalid or an error occurs, it returns a 401 or 400 response.
    Note: `spotify_auth` must be passed as keyword argument in controller function otherwise will error

    Args:
        f (function): The Flask route handler to be decorated.

    Returns:
        function: The decorated function with `spotify_auth` passed as a keyword argument.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            spotify_auth = validate_session(request.cookies)
        except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
            current_app.logger.error("Invalid credentials: " + str(e))
            return {"error": "Invalid credentials"}, 401
        except Exception as e:
            current_app.logger.error("Invalid request: " + str(e))
            return {"error": "Invalid request"}, 400
        
        # If validation succeeds, pass the Spotify auth object to the decorated function.
        return f(*args, spotify_auth=spotify_auth, **kwargs)
    return decorated
