from datetime import datetime, timedelta, timezone
from tests import client, env_patch
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

from database import database

from mock_responses import *

test_expiry = datetime.now(timezone.utc) + timedelta(hours=1)


def test_get_playlists_success(mocker, client, env_patch):
    """
    Successful GET Playlists
    """
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value={
                            "access_token": "accesstokenfromspotify",
                            "refresh_token": "refreshtokenfromspotify"
                        }
                        )
    mocker.patch.object(Spotify, "current_user",
                        return_value=mock_user_response
                        )
    mocker.patch.object(Spotify, "current_user_playlists",
                        return_value=mock_user_playlists_sample
                        )
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)

    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope",
                            "expiry": test_expiry
                        }
                        )
    mocker.patch.object(database, "find_and_update_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope",
                            "expiry": test_expiry
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.get('/api/playlist/me')
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["all_playlists"] is not None
    # Number of playlists returned from spotify + one for Liked Tracks
    assert len(response_json["all_playlists"]) == 2
    assert "user_shuffle_counter" not in response_json


def test_get_playlists_with_stats_user_tracker_enabled_success(mocker, client, env_patch):
    """
    Successful GET Playlists with include-stats=true and user tracker enabled
    """
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value={
                            "access_token": "accesstokenfromspotify",
                            "refresh_token": "refreshtokenfromspotify"
                        }
                        )
    mocker.patch.object(Spotify, "current_user",
                        return_value=mock_user_response
                        )
    mocker.patch.object(Spotify, "current_user_playlists",
                        return_value=mock_user_playlists_sample
                        )
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)

    mocker.patch.object(database, "find_user",
                        return_value={
                            "user_id": "user_id",
                            "user_attributes": {
                                  "trackers_enabled": True
                            }
                        }
                        )
    mocker.patch.object(database, "find_shuffle_counter",
                        return_value={
                            "user_id": "user_id",
                            "playlist_count": 2,
                            "track_count": 2,
                        }
                        )
    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope",
                            "expiry": test_expiry
                        }
                        )
    mocker.patch.object(database, "find_and_update_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope",
                            "expiry": test_expiry
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.get('/api/playlist/me?include-stats=true')
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["all_playlists"] is not None
    # Number of playlists returned from spotify + one for Liked Tracks
    assert len(response_json["all_playlists"]) == 2
    assert response_json["user_shuffle_counter"] is not None
    assert response_json["user_shuffle_counter"]["playlist_count"] == 2
    assert response_json["user_shuffle_counter"]["track_count"] == 2


def test_get_playlists_with_stats_user_tracker_disabled_success(mocker, client, env_patch):
    """
    Successful GET Playlists with include-stats=true and user tracker disabled
    """
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value={
                            "access_token": "accesstokenfromspotify",
                            "refresh_token": "refreshtokenfromspotify"
                        }
                        )
    mocker.patch.object(Spotify, "current_user",
                        return_value=mock_user_response
                        )
    mocker.patch.object(Spotify, "current_user_playlists",
                        return_value=mock_user_playlists_sample
                        )
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)

    mocker.patch.object(database, "find_user",
                        return_value={
                            "user_id": "user_id",
                            "user_attributes": {
                                  "trackers_enabled": False
                            }
                        }
                        )

    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope",
                            "expiry": test_expiry
                        }
                        )
    mocker.patch.object(database, "find_and_update_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope",
                            "expiry": test_expiry
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.get('/api/playlist/me?include-stats=true')
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["all_playlists"] is not None
    # Number of playlists returned from spotify + one for Liked Tracks
    assert len(response_json["all_playlists"]) == 2
    assert "user_shuffle_counter" not in response_json


def test_get_playlists_failure_cookies_invalid(mocker, client, env_patch):
    """
    Failure GET Playlists
    Request access token structure invalid
    """
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value=None
                        )
    mocker.patch.object(Spotify, "current_user",
                        return_value=mock_user_response
                        )
    mocker.patch.object(Spotify, "current_user_playlists",
                        return_value=mock_user_playlists_sample
                        )

    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope",
                            "expiry": test_expiry
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.get('/api/playlist/me')
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None


def test_get_playlists_failure_missing_cookies_failure(mocker, client, env_patch):
    """
    Failure GET Playlists
    Request missing cookies
    """
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value={
                            "access_token": "access token from spotify",
                            "refresh_token": "access token from spotify"
                        }
                        )
    mocker.patch.object(Spotify, "current_user",
                        return_value=mock_user_response
                        )
    mocker.patch.object(Spotify, "current_user_playlists",
                        return_value=mock_user_playlists_sample
                        )

    response = client.get('/api/playlist/me')
    response_json = response.get_json()
    assert response.status_code == 401
    assert response_json == {
        "error": "Invalid credentials"
    }


def test_get_playlists_failure_upstream_spotify_error(mocker, client, env_patch):
    """
    Failure GET Playlists
    Error from upstream Spotify call
    """
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value={
                            "access_token": "access token from spotify",
                            "refresh_token": "access token from spotify"
                        }
                        )
    mocker.patch.object(Spotify, "current_user",
                        return_value=mock_user_response
                        )
    mocker.patch.object(Spotify, "current_user_playlists",
                        return_value={"error": "spotify error"}
                        )

    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope",
                            "expiry": test_expiry
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.get('/api/playlist/me')
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None
