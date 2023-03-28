from datetime import datetime, timedelta, timezone
import uuid
import hashlib

from database import database
from exceptions.custom_exceptions import SessionExpired, SessionIdNone, SessionIdNotFound


def generate_session_id():
    """
    Generate random uuid for session id
    """
    return str(uuid.uuid4())


def generate_hashed_session_id(session_id):
    """
    Create hash from session id
    """
    if session_id == None:
        raise SessionIdNone(
            "Cannot generate hashed session id - session_id is None")
    return hashlib.sha256(session_id.encode('utf-8')).hexdigest()


def remove_session_entry(session_id):
    database.delete_session(generate_hashed_session_id(session_id))


def validate_session(cookies):
    """
    Validate session and return spotify auth if valid
    """
    session_id = cookies.get("trueshuffle-sessionId")

    # Find session entry with hashed session id
    session_entry = database.find_session(
        generate_hashed_session_id(session_id))
    if session_entry is None:
        raise SessionIdNotFound("Unable to find session")

    # Check session entry contains expected attributes
    if ("user_id" not in session_entry
            or "access_token" not in session_entry
            or "refresh_token" not in session_entry
            or "expires_at" not in session_entry
            or "scope" not in session_entry
            or "expiry" not in session_entry
        ):
        raise Exception("Session entry is invalid")

    # Check session expiry
    if session_entry["expiry"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        remove_session_entry(session_id)
        raise SessionExpired("Session expired")

    # Return spotify auth attributes
    return {
        "access_token": session_entry["access_token"],
        "refresh_token": session_entry["refresh_token"],
        "expires_at": session_entry["expires_at"],
        "scope": session_entry["scope"],
        "token_type": "Bearer"
    }


def extend_session_expiry(current_app, response, cookies):
    """
    Extend session expiry of cookies and database entry
    """
    session_id = cookies.get("trueshuffle-sessionId")
    session_expiry = datetime.now(timezone.utc) + timedelta(hours=1)

    # Update cookie
    response.set_cookie(key="trueshuffle-sessionId",
                            value=session_id,
                            httponly=True,
                            domain=current_app.config["COOKIE_DOMAIN"],
                            samesite='None',
                            secure=True,
                            expires=session_expiry
                        )
    response.set_cookie(key="trueshuffle-auth",
                        value="true",
                        domain=current_app.config["COOKIE_DOMAIN"],
                        samesite='None',
                        secure=True,
                        expires=session_expiry
                        )

    # Update database session entry
    entry_expiry_update = dict()
    entry_expiry_update["expiry"] = session_expiry
    session_response = database.find_and_update_session(
        generate_hashed_session_id(session_id), entry_expiry_update)
