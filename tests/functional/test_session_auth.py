from datetime import datetime, timedelta, timezone

import pymongo
from tests import client, env_patch
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

from database import database

from mock_responses import *

test_expiry = datetime.now(timezone.utc) + timedelta(hours=1)


def test_session_cookie_valid_success(mocker, client, env_patch):
    """
    Successful GET Playlists - Session cookie valid
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
    assert response.status_code == 200


def test_session_cookie_invalid_failure(mocker, client, env_patch):
    """
    Failure GET Playlists - Session cookie invalid - session id not found in database
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
                        return_value=None
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'invalidSessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.get('/api/playlist/me')
    assert response.status_code == 401


def test_session_cookie_missing_failure(mocker, client, env_patch):
    """
    Failure GET Playlists - Session cookie missing
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
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.get('/api/playlist/me')
    assert response.status_code == 401


def test_session_expired_expired_failure(mocker, client, env_patch):
    """
    Failure GET Playlists - Session expired
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
                            "expiry": datetime.now(timezone.utc) - timedelta(hours=1)
                        }
                        )
    mocker.patch.object(database, "delete_session",
                        return_value={
                            "count": "1"
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.get('/api/playlist/me')
    assert response.status_code == 401


def test_session_database_connection_error_failure(mocker, client, env_patch):
    """
    Failure GET Playlists - Database connection error
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
                        return_value=pymongo.errors.ConnectionFailure
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.get('/api/playlist/me')
    assert response.status_code == 400
