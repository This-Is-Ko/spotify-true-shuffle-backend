from tests import client, env_patch
import time
import datetime

from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from database import database
from mock_responses import *
from mock_requests import *

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"
SPOTIFY_PLAYLIST_URL = "open.spotify.com/playlist/spotifyPlaylistUrl"


shuffle_request = {
    "playlist_id": "playlist_id0",
    "playlist_name": "playlist_name0"
}

all_user_playlists_response_sample = {
    "items": [
        {
            "name": "playlist0",
            "id": "playlist0"
        },
        {
            "name": "playlist1",
            "id": "playlist1"
        },
        {
            "name": SHUFFLED_PLAYLIST_PREFIX + "playlist1",
            "id": "playlist1"
        }
    ]
}

empty_all_user_playlists_response_sample = {
    "items": [
    ]
}

create_user_playlist_response = {
    "id": "new_playlist_id",
    "external_urls": {
        "spotify": SPOTIFY_PLAYLIST_URL
    }
}

playlist_add_items_response = {
    "snapshot_id": "snapshot_id_0"
}


def test_create_shuffled_playlist_success(mocker, client, env_patch):
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value=spotify_auth_sample)
    mocker.patch.object(
        Spotify, "current_user_saved_tracks", return_value=mock_tracks_response)
    mocker.patch.object(
        Spotify, "playlist_items", side_effect=[mock_tracks_response, empty_all_user_playlists_response_sample])
    mocker.patch.object(
        Spotify, "current_user_playlists", return_value=all_user_playlists_response_sample)
    mocker.patch.object(
        Spotify, "current_user_unfollow_playlist", return_value=True)
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)
    mocker.patch.object(
        Spotify, "user_playlist_create", return_value=create_user_playlist_response)
    mocker.patch.object(
        Spotify, "playlist_add_items", return_value=playlist_add_items_response)
    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope"
                        }
                        )
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
                            "user_id": "overall_counter",
                            "playlist_count": 0,
                            "track_count": 0,
                        }
                        )
    mocker.patch.object(database, "find_and_update_shuffle_counter",
                        return_value={
                            "user_id": "overall_counter",
                            "playlist_count": 0,
                            "track_count": 0,
                        }
                        )
    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope"
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.post('/api/playlist/shuffle', json=shuffle_request)
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["playlist_uri"] == SPOTIFY_PLAYLIST_URL
    assert response_json["num_of_tracks"] == 2
    assert response_json["creation_time"] is not None


def test_create_shuffled_spotify_auth_error_failure(mocker, client, env_patch):
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value=None)
    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope"
                        }
                        )
    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope"
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.post('/api/playlist/shuffle', json=shuffle_request)
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json == {
        "error": "Invalid token"
    }


def test_create_shuffled_playlist_playlist_name_missing_failure(mocker, client, env_patch):
    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope"
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    invalid_shuffle_request = {
        "playlist_id": "playlist_id0"
    }
    response = client.post('/api/playlist/shuffle',
                           json=invalid_shuffle_request)
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json == {
        "error": "Invalid request"
    }


def test_create_shuffled_playlist_playlist_id_missing_failure(mocker, client, env_patch):
    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope"
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    invalid_shuffle_request = {
        "playlist_name": "playlist_name0"
    }
    response = client.post('/api/playlist/shuffle',
                           json=invalid_shuffle_request)
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json == {
        "error": "Invalid request"
    }


def test_create_shuffled_playlist_cookies_missing_failure(mocker, client, env_patch):
    # Missing cookies

    invalid_shuffle_request = {
        "playlist_id": "playlist_id0",
        "playlist_name": "playlist_name0"
    }
    response = client.post('/api/playlist/shuffle',
                           json=invalid_shuffle_request)
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json == {
        "error": "Invalid request"
    }


def test_delete_shuffled_playlists_success(mocker, client, env_patch):
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value=spotify_auth_sample)
    mocker.patch.object(
        Spotify, "current_user_playlists", return_value=all_user_playlists_response_sample)
    mocker.patch.object(
        Spotify, "current_user_unfollow_playlist", return_value=True)
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)

    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope"
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.delete('/api/playlist/delete')
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json == {
        "status": "success",
        "deleted_playlists_count": 1
    }


def test_delete_shuffled_spotify_auth_error_failure(mocker, client, env_patch):
    mocker.patch.object(SpotifyOAuth, "validate_token",
                        return_value=None)
    mocker.patch.object(
        Spotify, "current_user_playlists", return_value=all_user_playlists_response_sample)
    mocker.patch.object(
        Spotify, "current_user_unfollow_playlist", return_value=True)
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)

    mocker.patch.object(database, "find_session",
                        return_value={
                            "user_id": "user_id",
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                            "expires_at": "expires_at",
                            "scope": "scope"
                        }
                        )
    # Init cookies
    client.set_cookie('localhost', 'trueshuffle-sessionId',
                      'sessionId')
    client.set_cookie('localhost', 'trueshuffle-auth',
                      'true')

    response = client.delete('/api/playlist/delete')
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json == {
        "error": "Invalid token"
    }


def test_delete_shuffled_playlists_spotify_auth_missing_failure(mocker, client, env_patch):
    # Missing cookies
    response = client.delete('/api/playlist/delete')
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json == {
        "error": "Invalid request"
    }
