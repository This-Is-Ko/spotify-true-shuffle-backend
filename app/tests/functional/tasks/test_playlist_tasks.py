from tests import client, env_patch
import time
from datetime import datetime, timedelta, timezone

from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from database import database

from tests.functional.helpers.mock_requests import *
from tests.functional.helpers.mock_responses import *
from tasks.playlist_tasks import shuffle_playlist

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

def test_shuffle_playlist_success(mocker, env_patch):
    # Prepare mocks
    mocker.patch("utils.util.update_task_progress", return_value=None)
    mocker.patch("utils.tracker_utils.update_user_trackers", return_value=None)
    mocker.patch("utils.tracker_utils.update_overall_trackers", return_value=None)
    mocker.patch.object(Spotify, "current_user_saved_tracks", return_value=mock_tracks_response)
    mocker.patch.object(Spotify, "playlist_items", side_effect=[mock_tracks_response, empty_all_user_playlists_response_sample])
    mocker.patch.object(Spotify, "current_user_playlists", return_value=all_user_playlists_response_sample)
    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)
    mocker.patch.object(Spotify, "user_playlist_create", return_value=create_user_playlist_response)
    mocker.patch.object(Spotify, "playlist_add_items", return_value=playlist_add_items_response)
    mocker.patch.object(database, "find_user",
        return_value={
            "user_id": "user_id",
            "user_attributes": {
                "trackers_enabled": True
            }
        }
    )

    response = shuffle_playlist(spotify_auth_sample, "playlist_id", "playlist_name")

    assert response["status"] == "success"
    assert response["playlist_uri"] == SPOTIFY_PLAYLIST_URL
    assert response["num_of_tracks"] == 2
    assert response["creation_time"] is not None


def test_shuffle_playlist_shuffled_playlist_exists_success(mocker, env_patch):
    # Prepare mocks
    mocker.patch("utils.util.update_task_progress", return_value=None)
    mocker.patch("utils.tracker_utils.update_user_trackers", return_value=None)
    mocker.patch("utils.tracker_utils.update_overall_trackers", return_value=None)
    mocker.patch.object(Spotify, "current_user_saved_tracks", return_value=mock_tracks_response)
    mocker.patch.object(Spotify, "playlist_items", side_effect=[mock_tracks_response, empty_all_user_playlists_response_sample])
    mocker.patch.object(Spotify, "current_user_playlists", return_value=all_user_playlists_response_sample)
    mocker.patch.object(Spotify, "current_user_unfollow_playlist", return_value=True)
    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)
    mocker.patch.object(Spotify, "user_playlist_create", return_value=create_user_playlist_response)
    mocker.patch.object(Spotify, "playlist_add_items", return_value=playlist_add_items_response)
    mocker.patch.object(database, "find_user",
        return_value={
            "user_id": "user_id",
            "user_attributes": {
                "trackers_enabled": True
            }
        }
    )

    response = shuffle_playlist(spotify_auth_sample, "playlist_id", "playlist1")

    assert response["status"] == "success"
    assert response["playlist_uri"] == SPOTIFY_PLAYLIST_URL
    assert response["num_of_tracks"] == 2
    assert response["creation_time"] is not None

    
def test_shuffle_playlist_user_not_found_success(mocker, env_patch):
    # Cannot update trackers however shuffle can still proceed
    # Prepare mocks
    mocker.patch("utils.util.update_task_progress", return_value=None)
    mocker.patch("utils.tracker_utils.update_user_trackers", return_value=None)
    mocker.patch("utils.tracker_utils.update_overall_trackers", return_value=None)
    mocker.patch.object(Spotify, "current_user_saved_tracks", return_value=mock_tracks_response)
    mocker.patch.object(Spotify, "playlist_items", side_effect=[mock_tracks_response, empty_all_user_playlists_response_sample])
    mocker.patch.object(Spotify, "current_user_playlists", return_value=all_user_playlists_response_sample)
    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)
    mocker.patch.object(Spotify, "user_playlist_create", return_value=create_user_playlist_response)
    mocker.patch.object(Spotify, "playlist_add_items", return_value=playlist_add_items_response)
    mocker.patch.object(database, "find_user",return_value=None)

    response = shuffle_playlist(spotify_auth_sample, "playlist_id", "playlist_name")

    assert response["status"] == "success"
    assert response["playlist_uri"] == SPOTIFY_PLAYLIST_URL
    assert response["num_of_tracks"] == 2
    assert response["creation_time"] is not None
    

def test_shuffle_playlist_playlist_tracks_empty_failure(mocker, env_patch):
    # Prepare mocks
    mocker.patch("utils.util.get_tracks_from_playlist", return_value=None)

    response = shuffle_playlist(spotify_auth_sample, "playlist_id", "playlist_name")

    assert response["error"] == "No tracks found for playlist playlist_id"

