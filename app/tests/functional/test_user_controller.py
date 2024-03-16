from datetime import datetime, timedelta, timezone
from tests import client, env_patch
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

from mock_responses import *
from mock_requests import *
from database import database

test_expiry = datetime.now(timezone.utc) + timedelta(hours=1)


def test_get_user_analysis_success(mocker, client, env_patch):
    """
    Successful GET User Analysis
    """
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value={
                            "access_token": "access token from spotify",
                            "refresh_token": "access token from spotify"
                        }
                        )
    mocker.patch.object(Spotify, "current_user",
                        return_value=mock_user_response)
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)
    mocker.patch.object(
        Spotify, "current_user_saved_tracks", return_value=mock_tracks_response)
    mocker.patch.object(
        Spotify, "audio_features", return_value=mock_audio_features_response)

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

    response = client.get('/api/user/analysis')
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["most_common_artists"] is not None
    assert response_json["most_common_albums"] is not None
    assert response_json["most_common_genre"] is not None
    assert response_json["total_length"] is not None
    assert response_json["average_track_length"] is not None
    # Number of playlists returned from spotify + one for Liked Tracks
    assert len(response_json["most_common_artists"]) == 2


def test_get_user_analysis_empty_liked_songs_success(mocker, client, env_patch):
    """
    Successful GET User Analysis - empty 
    """
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value={
                            "access_token": "access token from spotify",
                            "refresh_token": "access token from spotify"
                        }
                        )
    mocker.patch.object(Spotify, "current_user",
                        return_value=mock_user_response)
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)
    mocker.patch.object(
        Spotify, "current_user_saved_tracks", return_value=mock_no_liked_songs_tracks_response)

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

    response = client.get('/api/user/analysis')
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["most_common_artists"] is not None
    assert response_json["most_common_albums"] is not None
    assert response_json["most_common_genre"] is not None
    assert response_json["total_length"] is not None
    assert response_json["average_track_length"] is not None
    # Number of playlists returned from spotify + one for Liked Tracks
    assert len(response_json["most_common_artists"]) == 0


def test_get_user_analysis_spotify_auth_error_failure(mocker, client, env_patch):
    """
    Error during spotify auth
    """
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value=None
                        )
    mocker.patch.object(Spotify, "current_user",
                        return_value=mock_user_response
                        )
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)
    mocker.patch.object(
        Spotify, "current_user_saved_tracks", return_value=mock_tracks_response)

    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope",
                            "expiry": datetime.now(timezone.utc) + timedelta(hours=1)
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.get('/api/user/analysis')
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None
