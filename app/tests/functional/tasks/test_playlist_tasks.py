from tests import env_patch # noqa: F401

from spotipy import Spotify
from database import database

from tests.functional.helpers.mock_requests import *
from tests.functional.helpers.mock_responses import *
from tasks.playlist_tasks import shuffle_playlist, create_playlist_from_liked_tracks, update_track_statistics

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
            "id": "playlist0",
            "external_urls": {
                "spotify": SPOTIFY_PLAYLIST_URL
            }
        },
        {
            "name": "playlist1",
            "id": "playlist1",
            "external_urls": {
                "spotify": SPOTIFY_PLAYLIST_URL
            }
        },
        {
            "name": SHUFFLED_PLAYLIST_PREFIX + "playlist1",
            "id": "playlist1",
            "external_urls": {
                "spotify": SPOTIFY_PLAYLIST_URL
            }
        }
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


############ shuffle_playlist ################


def test_shuffle_playlist_success(mocker, env_patch):
    # Prepare mocks
    mocker.patch("utils.util.update_task_progress", return_value=None)
    mocker.patch("utils.tracker_utils.update_user_trackers", return_value=None)
    mocker.patch("utils.tracker_utils.update_overall_trackers", return_value=None)
    mocker.patch("tasks.playlist_tasks.update_track_statistics.delay", return_value=None)
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
    mocker.patch("tasks.playlist_tasks.update_track_statistics.delay", return_value=None)
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
    # Testcase where cannot update trackers however shuffle can still proceed
    # Prepare mocks
    mocker.patch("utils.util.update_task_progress", return_value=None)
    mocker.patch("utils.tracker_utils.update_user_trackers", return_value=None)
    mocker.patch("utils.tracker_utils.update_overall_trackers", return_value=None)
    mocker.patch("tasks.playlist_tasks.update_track_statistics.delay", return_value=None)
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


def test_shuffle_playlist_playlist_tracks_empty_failure(mocker, env_patch):
    # Prepare mocks
    mocker.patch("utils.util.get_tracks_from_playlist", return_value=None)

    response = shuffle_playlist(spotify_auth_sample, "playlist_id", "playlist_name")

    assert response["error"] == "No tracks found for playlist playlist_id"



############ create_playlist_from_liked_tracks ################


def test_create_playlist_from_liked_tracks_success(mocker, env_patch):
    # Prepare mocks
    mocker.patch("utils.util.update_task_progress", return_value=None)
    mocker.patch("utils.tracker_utils.update_user_trackers", return_value=None)
    mocker.patch("utils.tracker_utils.update_overall_trackers", return_value=None)
    mocker.patch.object(Spotify, "current_user_saved_tracks", side_effect=[mock_tracks_response, empty_all_user_playlists_response_sample])
    mocker.patch.object(Spotify, "playlist_items", side_effect=[mock_tracks_response, empty_all_user_playlists_response_sample])
    mocker.patch.object(Spotify, "current_user_playlists", return_value=all_user_playlists_response_sample)
    mocker.patch.object(Spotify, "me", return_value=mock_user_details_response)
    mocker.patch.object(Spotify, "user_playlist_create", return_value=create_user_playlist_response)
    mocker.patch.object(Spotify, "playlist_add_items", return_value=playlist_add_items_response)

    response = create_playlist_from_liked_tracks(spotify_auth_sample, "playlist_name")

    assert response["status"] == "success"
    assert response["playlist_uri"] == SPOTIFY_PLAYLIST_URL
    assert response["num_of_tracks"] == 2
    assert response["creation_time"] is not None


def test_screate_playlist_from_liked_tracks_tracks_empty_failure(mocker, env_patch):
    # Prepare mocks
    mocker.patch("utils.util.get_tracks_from_playlist", return_value=None)

    response = create_playlist_from_liked_tracks(spotify_auth_sample, "playlist_name")

    assert response["error"] == "No tracks found for user's liked songs"


############ update_track_statistics ################


def test_update_track_statistics_success(mocker, env_patch):
    # Prepare mocks
    mocker.patch.object(database, "update_track_statistics",
        return_value=None
    )

    test_tracks = [
        {
            "track_id": "track_001",
            "track_name": "Test Track 1",
            "artists": [
                {"artist_id": "artist_001", "artist_name": "Artist One"}
            ],
            "is_local": False
        },
        {
            "track_id": "track_002",
            "track_name": "Test Track 2",
            "artists": [
                {"artist_id": "artist_002", "artist_name": "Artist Two"},
                {"artist_id": "artist_003", "artist_name": "Artist Three"}
            ],
            "is_local": False
        },
        {
            "track_id": "track_003",
            "track_name": "Local Track (Ignored)",
            "artists": [
                {"artist_id": "artist_004", "artist_name": "Artist Four"}
            ],
            "is_local": True  # This track should be filtered out
        }
    ]

    response = update_track_statistics("test_user", test_tracks)
    assert response == 2


def test_update_track_statistics_all_tracks_are_is_local_true_success(mocker, env_patch):
    # Prepare mocks
    mocker.patch.object(database, "update_track_statistics",
        return_value=None
    )

    # Filter out all tracks as all are is_local
    test_tracks = [
        {
            "track_id": "track_001",
            "track_name": "Test Track 1",
            "artists": [
                {"artist_id": "artist_001", "artist_name": "Artist One"}
            ],
            "is_local": True
        },
        {
            "track_id": "track_002",
            "track_name": "Test Track 2",
            "artists": [
                {"artist_id": "artist_002", "artist_name": "Artist Two"},
                {"artist_id": "artist_003", "artist_name": "Artist Three"}
            ],
            "is_local": True
        },
        {
            "track_id": "track_003",
            "track_name": "Local Track (Ignored)",
            "artists": [
                {"artist_id": "artist_004", "artist_name": "Artist Four"}
            ],
            "is_local": True  # This track should be filtered out
        }
    ]

    response = update_track_statistics("test_user", test_tracks)
    assert response == 0


def test_update_track_statistics_empty_tracks_success(mocker, env_patch):
    # Prepare mocks
    mocker.patch.object(database, "update_track_statistics",
        return_value=None
    )

    # Filter out all tracks as all are is_local
    test_tracks = []

    response = update_track_statistics("test_user", test_tracks)
    assert response == 0