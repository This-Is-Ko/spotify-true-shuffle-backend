from datetime import datetime, timedelta, timezone
from tests import client, env_patch  # noqa: F401

from database import database
from utils import auth_utils
from services import playlist_service
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from celery.result import AsyncResult
from tests.functional.helpers.mock_responses import mock_user_details_response

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

    mocker.patch.object(
        database,
        "find_and_update_session",
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


"""
Success scenarios - GET /api/playlist/shuffle/state/<id>
"""


def test_get_shuffle_state_progress_success(mocker, client, env_patch):  # noqa: F811
    """
    Successful GET shuffle state request - PROGRESS state
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

    mocker.patch.object(SpotifyOAuth, "validate_token", return_value={
        "access_token": "accesstokenfromspotify",
        "refresh_token": "refreshtokenfromspotify"
    })

    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)

    # Mock AsyncResult for PROGRESS state
    mock_result = mocker.Mock(spec=AsyncResult)
    mock_result.state = "PROGRESS"
    mock_result.info = {"progress": 75}
    mocker.patch("tasks.task_state.AsyncResult", return_value=mock_result)

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform GET request
    response = client.get('/api/playlist/shuffle/state/task_id_123')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["state"] == "PROGRESS"
    assert "progress" in response_json


def test_get_shuffle_state_success_success(mocker, client, env_patch):  # noqa: F811
    """
    Successful GET shuffle state request - SUCCESS state
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

    mocker.patch.object(SpotifyOAuth, "validate_token", return_value={
        "access_token": "accesstokenfromspotify",
        "refresh_token": "refreshtokenfromspotify"
    })

    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)

    # Mock AsyncResult for SUCCESS state
    mock_result = mocker.Mock(spec=AsyncResult)
    mock_result.state = "SUCCESS"
    mock_result.get = mocker.Mock(return_value={"status": "success", "playlist_id": "new_playlist_id"})
    mock_result.forget = mocker.Mock()
    mocker.patch("tasks.task_state.AsyncResult", return_value=mock_result)

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform GET request
    response = client.get('/api/playlist/shuffle/state/task_id_123')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["state"] == "SUCCESS"
    assert "result" in response_json


def test_get_shuffle_state_pending_success(mocker, client, env_patch):  # noqa: F811
    """
    Successful GET shuffle state request - PENDING state
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

    mocker.patch.object(SpotifyOAuth, "validate_token", return_value={
        "access_token": "accesstokenfromspotify",
        "refresh_token": "refreshtokenfromspotify"
    })

    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)

    # Mock AsyncResult for PENDING state
    mock_result = mocker.Mock(spec=AsyncResult)
    mock_result.state = "PENDING"
    mock_result.ready = mocker.Mock(return_value=False)
    mock_result.successful = mocker.Mock(return_value=False)
    mocker.patch("tasks.task_state.AsyncResult", return_value=mock_result)

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform GET request
    response = client.get('/api/playlist/shuffle/state/task_id_123')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["state"] == "PENDING"
    assert "ready" in response_json


"""
Failure scenarios - GET /api/playlist/shuffle/state/<id>
"""


def test_get_shuffle_state_failure_invalid_auth(mocker, client, env_patch):  # noqa: F811
    """
    Failure GET shuffle state request - invalid auth
    """
    mocker.patch.object(
        database,
        "find_session",
        return_value=None
    )

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform GET request
    response = client.get('/api/playlist/shuffle/state/task_id_123')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 401
    assert response_json["error"] == "Invalid credentials"


def test_get_shuffle_state_failure_missing_cookies(mocker, client, env_patch):  # noqa: F811
    """
    Failure GET shuffle state request - missing cookies
    """
    # Perform GET request without cookies
    response = client.get('/api/playlist/shuffle/state/task_id_123')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 401
    assert response_json["error"] == "Invalid credentials"


"""
Success scenarios - DELETE /api/playlist/delete
"""


def test_delete_shuffled_playlists_success(mocker, client, env_patch):  # noqa: F811
    """
    Successful DELETE shuffled playlists request
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

    mocker.patch.object(
        database,
        "find_and_update_session",
        return_value={
            "user_id": "user_id",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": "expires_at",
            "scope": "scope",
            "session_expiry": test_expiry
        }
    )

    mocker.patch.object(SpotifyOAuth, "validate_token", return_value={
        "access_token": "accesstokenfromspotify",
        "refresh_token": "refreshtokenfromspotify"
    })

    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)

    mocker.patch.object(Spotify, "current_user_playlists", return_value={
        "items": [
            {"name": "[Shuffled] Playlist 1", "id": "playlist1"},
            {"name": "Normal Playlist", "id": "playlist2"},
            {"name": "[Shuffled] Playlist 2", "id": "playlist3"}
        ]
    })

    mocker.patch.object(Spotify, "current_user_unfollow_playlist", return_value=None)

    mocker.patch.object(playlist_service, "delete_all_shuffled_playlists", return_value={
        "status": "success",
        "deleted_playlists_count": 2
    })

    mocker.patch.object(auth_utils, "extend_session_expiry", return_value=None)

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform DELETE request
    response = client.delete('/api/playlist/delete')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["deleted_playlists_count"] == 2


def test_delete_shuffled_playlists_no_shuffled_success(mocker, client, env_patch):  # noqa: F811
    """
    Successful DELETE shuffled playlists request - no shuffled playlists
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

    mocker.patch.object(SpotifyOAuth, "validate_token", return_value={
        "access_token": "accesstokenfromspotify",
        "refresh_token": "refreshtokenfromspotify"
    })

    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)

    mocker.patch.object(playlist_service, "delete_all_shuffled_playlists", return_value={
        "status": "success",
        "deleted_playlists_count": 0
    })

    mocker.patch.object(auth_utils, "extend_session_expiry", return_value=None)

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform DELETE request
    response = client.delete('/api/playlist/delete')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["deleted_playlists_count"] == 0


"""
Failure scenarios - DELETE /api/playlist/delete
"""


def test_delete_shuffled_playlists_failure_invalid_auth(mocker, client, env_patch):  # noqa: F811
    """
    Failure DELETE shuffled playlists request - invalid auth
    """
    mocker.patch.object(
        database,
        "find_session",
        return_value=None
    )

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform DELETE request
    response = client.delete('/api/playlist/delete')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 401
    assert response_json["error"] == "Invalid credentials"


def test_delete_shuffled_playlists_failure_missing_cookies(mocker, client, env_patch):  # noqa: F811
    """
    Failure DELETE shuffled playlists request - missing cookies
    """
    # Perform DELETE request without cookies
    response = client.delete('/api/playlist/delete')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 401
    assert response_json["error"] == "Invalid credentials"


def test_delete_shuffled_playlists_failure_exception(mocker, client, env_patch):  # noqa: F811
    """
    Failure DELETE shuffled playlists request - service error
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

    mocker.patch.object(playlist_service, "delete_all_shuffled_playlists", side_effect=Exception("Service error"))

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform DELETE request
    response = client.delete('/api/playlist/delete')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json["error"] == "Unable to delete shuffled playlists"


"""
Success scenarios - POST /api/playlist/share/liked-tracks
"""


def test_queue_liked_tracks_playlist_with_name_success(mocker, client, env_patch):  # noqa: F811
    """
    Successful POST queue liked tracks playlist request - with playlist name
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

    mocker.patch.object(
        database,
        "find_and_update_session",
        return_value={
            "user_id": "user_id",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": "expires_at",
            "scope": "scope",
            "session_expiry": test_expiry
        }
    )

    mocker.patch.object(playlist_service, "queue_create_playlist_from_liked_tracks", return_value={
        "create_liked_playlist_id": "task_id_123"
    })

    mocker.patch.object(auth_utils, "extend_session_expiry", return_value=None)

    request_body = {"playlist_name": "My Liked Tracks Playlist"}

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform POST request
    response = client.post('/api/playlist/share/liked-tracks', json=request_body)

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert "create_liked_playlist_id" in response_json
    assert response_json["create_liked_playlist_id"] == "task_id_123"


def test_queue_liked_tracks_playlist_without_name_success(mocker, client, env_patch):  # noqa: F811
    """
    Successful POST queue liked tracks playlist request - without playlist name (default)
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

    mocker.patch.object(
        database,
        "find_and_update_session",
        return_value={
            "user_id": "user_id",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": "expires_at",
            "scope": "scope",
            "session_expiry": test_expiry
        }
    )

    mocker.patch.object(playlist_service, "queue_create_playlist_from_liked_tracks", return_value={
        "create_liked_playlist_id": "task_id_456"
    })

    mocker.patch.object(auth_utils, "extend_session_expiry", return_value=None)

    request_body = {}

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform POST request
    response = client.post('/api/playlist/share/liked-tracks', json=request_body)

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert "create_liked_playlist_id" in response_json
    assert response_json["create_liked_playlist_id"] == "task_id_456"


"""
Failure scenarios - POST /api/playlist/share/liked-tracks
"""


def test_queue_liked_tracks_playlist_failure_invalid_auth(mocker, client, env_patch):  # noqa: F811
    """
    Failure POST queue liked tracks playlist request - invalid auth
    """
    mocker.patch.object(
        database,
        "find_session",
        return_value=None
    )

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    request_body = {"playlist_name": "My Liked Tracks"}

    # Perform POST request
    response = client.post('/api/playlist/share/liked-tracks', json=request_body)

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 401
    assert response_json["error"] == "Invalid credentials"


def test_queue_liked_tracks_playlist_failure_missing_cookies(mocker, client, env_patch):  # noqa: F811
    """
    Failure POST queue liked tracks playlist request - missing cookies
    """
    request_body = {"playlist_name": "My Liked Tracks"}

    # Perform POST request without cookies
    response = client.post('/api/playlist/share/liked-tracks', json=request_body)

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 401
    assert response_json["error"] == "Invalid credentials"


def test_queue_liked_tracks_playlist_failure_exception(mocker, client, env_patch):  # noqa: F811
    """
    Failure POST queue liked tracks playlist request - service error
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

    mocker.patch.object(playlist_service, "queue_create_playlist_from_liked_tracks", side_effect=Exception("Service error"))

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    request_body = {"playlist_name": "My Liked Tracks"}

    # Perform POST request
    response = client.post('/api/playlist/share/liked-tracks', json=request_body)

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json["error"] == "Unable to create share playlist"


"""
Success scenarios - GET /api/playlist/share/liked-tracks/<id>
"""


def test_get_liked_tracks_playlist_state_progress_success(mocker, client, env_patch):  # noqa: F811
    """
    Successful GET liked tracks playlist state request - PROGRESS state
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

    mocker.patch.object(SpotifyOAuth, "validate_token", return_value={
        "access_token": "accesstokenfromspotify",
        "refresh_token": "refreshtokenfromspotify"
    })

    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)

    # Mock AsyncResult for PROGRESS state
    mock_result = mocker.Mock(spec=AsyncResult)
    mock_result.state = "PROGRESS"
    mock_result.info = {"progress": 60}
    mocker.patch("tasks.task_state.AsyncResult", return_value=mock_result)

    mocker.patch.object(auth_utils, "extend_session_expiry", return_value=None)

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform GET request
    response = client.get('/api/playlist/share/liked-tracks/task_id_123')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["state"] == "PROGRESS"
    assert "progress" in response_json


def test_get_liked_tracks_playlist_state_success_success(mocker, client, env_patch):  # noqa: F811
    """
    Successful GET liked tracks playlist state request - SUCCESS state
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

    mocker.patch.object(SpotifyOAuth, "validate_token", return_value={
        "access_token": "accesstokenfromspotify",
        "refresh_token": "refreshtokenfromspotify"
    })

    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)

    # Mock AsyncResult for SUCCESS state
    mock_result = mocker.Mock(spec=AsyncResult)
    mock_result.state = "SUCCESS"
    mock_result.get = mocker.Mock(return_value={"status": "success", "playlist_id": "new_playlist_id"})
    mock_result.forget = mocker.Mock()
    mocker.patch("tasks.task_state.AsyncResult", return_value=mock_result)

    mocker.patch.object(auth_utils, "extend_session_expiry", return_value=None)

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform GET request
    response = client.get('/api/playlist/share/liked-tracks/task_id_123')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["state"] == "SUCCESS"
    assert "result" in response_json


"""
Failure scenarios - GET /api/playlist/share/liked-tracks/<id>
"""


def test_get_liked_tracks_playlist_state_failure_invalid_auth(mocker, client, env_patch):  # noqa: F811
    """
    Failure GET liked tracks playlist state request - invalid auth
    """
    mocker.patch.object(
        database,
        "find_session",
        return_value=None
    )

    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId', 'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth', 'true')

    # Perform GET request
    response = client.get('/api/playlist/share/liked-tracks/task_id_123')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 401
    assert response_json["error"] == "Invalid credentials"


def test_get_liked_tracks_playlist_state_failure_missing_cookies(mocker, client, env_patch):  # noqa: F811
    """
    Failure GET liked tracks playlist state request - missing cookies
    """
    # Perform GET request without cookies
    response = client.get('/api/playlist/share/liked-tracks/task_id_123')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 401
    assert response_json["error"] == "Invalid credentials"
