import json
from bson import json_util
import uuid
import hashlib

from database import database
from exceptions.custom_exceptions import SessionIdNone, SessionIdNotFound


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
            ):
        raise Exception("Session entry is invalid")

    # Return spotify auth attributes
    return {
        "access_token": session_entry["access_token"],
        "refresh_token": session_entry["refresh_token"],
        "expires_at": session_entry["expires_at"],
        "scope": session_entry["scope"],
        "token_type": "Bearer"
    }
