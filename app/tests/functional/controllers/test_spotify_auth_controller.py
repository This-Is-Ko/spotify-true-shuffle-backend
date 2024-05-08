from tests import client, env_patch
from spotipy.oauth2 import SpotifyOAuth
from utils import auth_utils
from database import database
from spotipy import Spotify

from tests.functional.helpers.mock_requests import *
from tests.functional.helpers.mock_responses import *


def test_get_spotify_uri_success(client, env_patch):
    """
    Successful GET Spotify Uri
    """
    response = client.get('/api/spotify/auth/login')
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["loginUri"] is not None


def test_handle_auth_code_success(mocker, client, env_patch):
    """
    Successful POST Handle Auth Code
    """
    mocker.patch.object(SpotifyOAuth, "get_access_token",
                        return_value={
                            "access_token": "accesstokenfromspotify",
                            "refresh_token": "refreshtokenfromspotify",
                            "expires_at": 12345,
                            "scope": "scopefromspotify"
                        }
                        )
    mocker.patch.object(SpotifyOAuth, "validate_token", return_value={
                            "access_token": "accesstokenfromspotify",
                            "refresh_token": "refreshtokenfromspotify"
                        }
                        )
    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)
    mocker.patch.object(auth_utils, "generate_session_id",
                        return_value="sessionId"
                        )
    mocker.patch.object(auth_utils, "generate_hashed_session_id",
                        return_value="hashedSessionId"
                        )
    mocker.patch.object(database, "find_and_update_user",
                        return_value={
                            "user_id": "userId"
                        }
                        )
    mocker.patch.object(database, "find_and_update_session",
                        return_value={
                            "user_id": "userId",
                            "session_id": "hashedSessionId",
                            "access_token": "accesstokenfromspotify",
                            "refresh_token": "refreshtokenfromspotify",
                            "expires_at": 12345,
                            "scope": "scopefromspotify"
                        }
                        )
    response = client.post('/api/spotify/auth/code', json={"code": "1234"})
    assert response.status_code == 200
    assert response.headers['Set-Cookie'] is not None

    expected_cookies = [
        'trueshuffle-sessionId=',
        'trueshuffle-auth=true'
    ]
    success_count = 0
    for expected in expected_cookies:
        for header in response.headers:
            if expected in header[1]:
                success_count += 1
                break

    assert success_count == 2


def test_handle_auth_code_failure_missing_code(mocker, client, env_patch):
    """
    Failure POST Handle Auth Code
    Code missing
    """
    response = client.post('/api/spotify/auth/code')
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None


def test_handle_auth_code_failure_upstream_spotify_error(mocker, client, env_patch):
    """
    Failure POST Handle Auth Code
    Error from upstream Spotify
    """
    mocker.patch.object(SpotifyOAuth, "get_access_token",
                        return_value={
                            "error": "spotify error",
                        }
                        )
    response = client.post('/api/spotify/auth/code', json={"code": "1234"})
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None


def test_logout_success(mocker, client, env_patch):
    """
    Success POST Logout
    """
    mocker.patch.object(database, "delete_session",
                        return_value={
                            "count": "1"
                        }
                        )
    response = client.post('/api/spotify/auth/logout')
    assert response.status_code == 200
    assert response.headers['Set-Cookie'] is not None

    expected_cookies = [
        'trueshuffle-sessionId=',
        'trueshuffle-auth='
    ]
    success_count = 0
    for expected in expected_cookies:
        for header in response.headers:
            if expected in header[1]:
                success_count += 1
                break

    assert success_count == 2


def test_logout_session_not_found_success(mocker, client, env_patch):
    """
    Success POST Logout session entry not found in database
    Note: Expire cookies regardless of delete status
    """
    mocker.patch.object(database, "delete_session",
                        return_value=None
                        )
    response = client.post('/api/spotify/auth/logout')
    assert response.status_code == 200
    assert response.headers['Set-Cookie'] is not None

    expected_cookies = [
        'trueshuffle-sessionId=',
        'trueshuffle-auth='
    ]
    success_count = 0
    for expected in expected_cookies:
        for header in response.headers:
            if expected in header[1]:
                success_count += 1
                break

    assert success_count == 2
