from tests import client, env_patch
import time

from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"
SPOTIFY_PLAYLIST_URL = "open.spotify.com/playlist/spotifyPlaylistUrl"

spotify_access_info_sample = {
    "token_type": "Bearer",
    "access_token": "access token from spotify",
    "refresh_token": "access token from spotify",
    "expires_at": int(time.time()) + 3600,
    "scope": "playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read"
}

delete_request = {
    "spotify_access_info": spotify_access_info_sample
}

shuffle_request = {
    "spotify_access_info": spotify_access_info_sample,
    "playlist_id": "playlist_id0",
    "playlist_name": "playlist_name0"
}

tracks_response_sample = {
    "items": [
        {
            "track":
                {
                    "uri": "track_uri0"
                }
        },
        {
            "track":
                {
                    "uri": "track_uri1"
                }
        }
    ]
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

user_details_response_sample = {
    "id": "user_id"
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
                        return_value=spotify_access_info_sample)
    mocker.patch.object(
        Spotify, "current_user_saved_tracks", return_value=tracks_response_sample)
    mocker.patch.object(
        Spotify, "playlist_items", side_effect=[tracks_response_sample, empty_all_user_playlists_response_sample])
    mocker.patch.object(
        Spotify, "current_user_playlists", return_value=all_user_playlists_response_sample)
    mocker.patch.object(
        Spotify, "current_user_unfollow_playlist", return_value=True)
    mocker.patch.object(
        Spotify, "me", return_value=user_details_response_sample)
    mocker.patch.object(
        Spotify, "user_playlist_create", return_value=create_user_playlist_response)
    mocker.patch.object(
        Spotify, "playlist_add_items", return_value=playlist_add_items_response)
    mocker.patch("builtins.open", mocker.mock_open(read_data="99"))

    response = client.post('/api/playlist/shuffle', json=shuffle_request)
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json == {
        "status": "success",
        "playlist_uri": SPOTIFY_PLAYLIST_URL,
        "num_of_tracks": 2
    }


def test_create_shuffled_playlist_playlist_name_missing_failure(mocker, client, env_patch):
    invalid_shuffle_request = {
        "spotify_access_info": spotify_access_info_sample,
        "playlist_id": "playlist_id0",
    }
    response = client.post('/api/playlist/shuffle',
                           json=invalid_shuffle_request)
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json == {
        "error": "Invalid request"
    }


def test_create_shuffled_playlist_playlist_id_missing_failure(mocker, client, env_patch):
    invalid_shuffle_request = {
        "spotify_access_info": spotify_access_info_sample,
        "playlist_name": "playlist_name0"
    }
    response = client.post('/api/playlist/shuffle',
                           json=invalid_shuffle_request)
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json == {
        "error": "Invalid request"
    }


def test_create_shuffled_playlist_spotify_access_info_missing_failure(mocker, client, env_patch):
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
                        return_value=spotify_access_info_sample)
    mocker.patch.object(
        Spotify, "current_user_playlists", return_value=all_user_playlists_response_sample)
    mocker.patch.object(
        Spotify, "current_user_unfollow_playlist", return_value=True)

    response = client.post('/api/playlist/delete', json=delete_request)
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json == {
        "status": "success",
        "deleted_playlists_count": 1
    }


def test_delete_shuffled_playlists_spotify_access_info_missing_failure(mocker, client, env_patch):
    invalid_delete_request = {}
    response = client.post('/api/playlist/delete', json=invalid_delete_request)
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json == {
        "error": "Invalid request"
    }
