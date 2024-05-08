from flask import Flask
from tests import client, env_patch

from spotipy import Spotify
from database import database

from tests.functional.helpers.mock_requests import *
from tests.functional.helpers.mock_responses import *
from utils.util import get_tracks_from_playlist, create_new_playlist_with_tracks

SPOTIFY_PLAYLIST_URL = "open.spotify.com/playlist/spotifyPlaylistUrl"

create_user_playlist_response = {
    "id": "new_playlist_id",
    "external_urls": {
        "spotify": SPOTIFY_PLAYLIST_URL
    }
}

playlist_add_items_response = {
    "snapshot_id": "snapshot_id_0"
}

sample_tracks_list = [
    "sometrack0",
    "sometrack1",
    "sometrack2"
]

app = Flask('test')


############ get_tracks_from_playlist ################


def test_get_tracks_from_playlist_from_existing_playlist_success(mocker, env_patch):
    with app.app_context():
        # Prepare mocks
        mocker.patch("utils.util.update_task_progress", return_value=None)
        mocker.patch.object(Spotify, "playlist_items", side_effect=[mock_tracks_response, empty_all_user_playlists_response_sample])

        all_tracks = get_tracks_from_playlist(None, Spotify(), "playlist_id")

        assert len(all_tracks) == 2


def test_get_tracks_from_playlist_from_liked_songs_success(mocker, env_patch):
    with app.app_context():
        # Prepare mocks
        mocker.patch("utils.util.update_task_progress", return_value=None)
        mocker.patch.object(Spotify, "current_user_saved_tracks", side_effect=[mock_tracks_response, empty_all_user_playlists_response_sample])

        all_tracks = get_tracks_from_playlist(None, Spotify(), "likedTracks")

        assert len(all_tracks) == 2


def test_get_tracks_from_playlist_no_tracks_from_existing_playlist_success(mocker, env_patch):
    with app.app_context():
        # Prepare mocks
        mocker.patch("utils.util.update_task_progress", return_value=None)
        mocker.patch.object(Spotify, "playlist_items", side_effect=[empty_all_user_playlists_response_sample])

        all_tracks = get_tracks_from_playlist(None, Spotify(), "playlist_id")

        assert len(all_tracks) == 0


def test_get_tracks_from_playlist_no_tracks_from_liked_songs_success(mocker, env_patch):
    with app.app_context():
        # Prepare mocks
        mocker.patch("utils.util.update_task_progress", return_value=None)
        mocker.patch.object(Spotify, "current_user_saved_tracks", side_effect=[empty_all_user_playlists_response_sample])

        all_tracks = get_tracks_from_playlist(None, Spotify(), "likedTracks")

        assert len(all_tracks) == 0


def test_get_tracks_from_playlist_error_getting_playlist_items_failure(mocker, env_patch):
    with app.app_context():
        # Prepare mocks
        mocker.patch("utils.util.update_task_progress", return_value=None)
        mocker.patch.object(Spotify, "playlist_items", side_effect=Exception("playlist_items error"))

        try:
            all_tracks = get_tracks_from_playlist(None, Spotify(), "playlist_id")
        except Exception as e:
            assert str(e) == "playlist_items error"


def test_get_tracks_from_playlist_error_getting_liked_songs_failure(mocker, env_patch):
    with app.app_context():
        # Prepare mocks
        mocker.patch("utils.util.update_task_progress", return_value=None)
        mocker.patch.object(Spotify, "current_user_saved_tracks", side_effect=Exception("current_user_saved_tracks error"))

        try:
            all_tracks = get_tracks_from_playlist(None, Spotify(), "likedTracks")
        except Exception as e:
            assert str(e) == "current_user_saved_tracks error"




############ create_new_playlist_with_tracks ################


def test_create_new_playlist_with_tracks_success(mocker, env_patch):
    with app.app_context():
        # Prepare mocks
        mocker.patch("utils.util.update_task_progress", return_value=None)
        mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)
        mocker.patch.object(Spotify, "user_playlist_create", return_value=create_user_playlist_response)
        mocker.patch.object(Spotify, "playlist_add_items", return_value=playlist_add_items_response)

        response = create_new_playlist_with_tracks(None, Spotify(), "new_playlist_name", False, "playlist_description", sample_tracks_list)

        assert response["status"] == "success"
        assert response["playlist_uri"] == SPOTIFY_PLAYLIST_URL
        assert response["num_of_tracks"] == 3
        assert response["creation_time"] is not None

        
def test_create_new_playlist_with_tracks_empty_track_list_failure(mocker, env_patch):
    with app.app_context():
        # Prepare mocks

        response = create_new_playlist_with_tracks(None, Spotify(), "new_playlist_name", False, "playlist_description", [])

        assert response["error"] == "Unable to create new playlist / add tracks to playlist"


def test_create_new_playlist_with_tracks_error_getting_spotify_user_failure(mocker, env_patch):
    with app.app_context():
        # Prepare mocks
        mocker.patch("utils.util.update_task_progress", return_value=None)
        mocker.patch.object(Spotify, "me", side_effect=Exception("mocked error"))

        response = create_new_playlist_with_tracks(None, Spotify(), "new_playlist_name", False, "playlist_description", sample_tracks_list)

        assert response["error"] == "Unable to create new playlist / add tracks to playlist"


def test_create_new_playlist_with_tracks_error_initialising_playlist_failure(mocker, env_patch):
    with app.app_context():
        # Prepare mocks
        mocker.patch("utils.util.update_task_progress", return_value=None)
        mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)
        mocker.patch.object(Spotify, "user_playlist_create", side_effect=Exception("mocked error"))

        response = create_new_playlist_with_tracks(None, Spotify(), "new_playlist_name", False, "playlist_description", sample_tracks_list)

        assert response["error"] == "Unable to create new playlist / add tracks to playlist"


def test_create_new_playlist_with_tracks_error_adding_items_failure(mocker, env_patch):
    with app.app_context():
        # Prepare mocks
        mocker.patch("utils.util.update_task_progress", return_value=None)
        mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)
        mocker.patch.object(Spotify, "user_playlist_create", return_value=create_user_playlist_response)
        mocker.patch.object(Spotify, "playlist_add_items", side_effect=Exception("mocked error"))

        response = create_new_playlist_with_tracks(None, Spotify(), "new_playlist_name", False, "playlist_description", sample_tracks_list)

        assert response["error"] == "Unable to create new playlist / add tracks to playlist"
