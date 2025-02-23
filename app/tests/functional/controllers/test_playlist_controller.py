from datetime import datetime, timedelta, timezone
from tests import client, env_patch  # noqa: F401

from database import database
from utils import auth_utils
from services import playlist_service

test_expiry = datetime.now(timezone.utc) + timedelta(hours=4)


"""
Success scenarios - Queue shuffled playlist
"""


def test_queue_shuffle_playlist_success(mocker, client, env_patch):  # noqa: F811
    """
    Successful POST shuffle playlist request
    """
    mocker.patch.object(
        database,
        "find_session",
        return_value={
            "user_id": "user_id",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": "expires_at",
            "scope": "scope",
            "session_expiry": test_expiry
        }
    )
    
    mocker.patch.object(database, "find_and_update_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope",
                            "session_expiry": test_expiry
                        }
                        )

    # Mock the queue_create_shuffled_playlist function
    mocker.patch.object(playlist_service,
                        "queue_create_shuffled_playlist",
                        return_value={"shuffle_task_id": "mocked_task_id"})

    # Mock session handling
    mocker.patch.object(auth_utils, "extend_session_expiry", return_value=None)

    request_body = {"playlist_id": "playlist_id", "playlist_name": "Test Playlist"}

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform POST request
    response = client.post('/api/playlist/shuffle', json=request_body)

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["shuffle_task_id"] == "mocked_task_id"
    assert "error" not in response_json


"""
Failure scenarios - Queue shuffled playlist
"""


def test_queue_shuffle_playlist_failure_invalid_schema_empty(mocker, client, env_patch):  # noqa: F811
    """
    Failure POST shuffle playlist request - invalid schema
    Empty json
    """
    mocker.patch.object(
        database,
        "find_session",
        return_value={
            "user_id": "user_id",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": "expires_at",
            "scope": "scope",
            "session_expiry": test_expiry
        }
    )

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform POST request with invalid schema
    response = client.post('/api/playlist/shuffle', json={})

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json["error"] == "Invalid request"


def test_queue_shuffle_playlist_failure_invalid_schema_playlist_id_missing(mocker, client, env_patch):  # noqa: F811
    """
    Failure POST shuffle playlist request - invalid schema
    playlist_id missing
    """
    mocker.patch.object(
        database,
        "find_session",
        return_value={
            "user_id": "user_id",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": "expires_at",
            "scope": "scope",
            "session_expiry": test_expiry
        }
    )

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    request_body = {"playlist_name": "Test Playlist"}

    # Perform POST request with invalid schema
    response = client.post('/api/playlist/shuffle', json=request_body)

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json["error"] == "Invalid request"


def test_queue_shuffle_playlist_failure_invalid_schema_playlist_name_missing(mocker, client, env_patch):  # noqa: F811
    """
    Failure POST shuffle playlist request - invalid schema
    playlist_name missing
    """
    mocker.patch.object(
        database,
        "find_session",
        return_value={
            "user_id": "user_id",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": "expires_at",
            "scope": "scope",
            "session_expiry": test_expiry
        }
    )

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    request_body = {"playlist_id": "playlist_id"}

    # Perform POST request with invalid schema
    response = client.post('/api/playlist/shuffle', json=request_body)

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json["error"] == "Invalid request"


def test_queue_shuffle_playlist_failure_exception(mocker, client, env_patch):  # noqa: F811
    """
    Failure POST shuffle playlist request - service error
    """
    mocker.patch.object(
        database,
        "find_session",
        return_value={
            "user_id": "user_id",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": "expires_at",
            "scope": "scope",
            "session_expiry": test_expiry
        }
    )

    # Mock the queue_create_shuffled_playlist function to raise an exception
    mocker.patch.object(playlist_service,
                        "queue_create_shuffled_playlist",
                        side_effect=Exception("Internal server error"))

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    request_body = {"playlist_id": "playlist_id", "playlist_name": "Test Playlist"}

    # Perform POST request
    response = client.post('/api/playlist/shuffle', json=request_body)

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json["error"] == "Unable to queue to create shuffled playlist"


def test_queue_shuffle_playlist_failure_invalid_auth(mocker, client, env_patch):  # noqa: F811
    """
    Failure POST shuffle playlist request - invalid auth
    """
    mocker.patch.object(
        database,
        "find_session",
        return_value=None
    )

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    request_body = {"playlist_id": "playlist_id", "playlist_name": "Test Playlist"}

    # Perform POST request with invalid auth
    response = client.post('/api/playlist/shuffle', json=request_body)

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 401
    assert response_json["error"] == "Invalid credentials"
