from tests import client, env_patch
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

from mock_responses import *
from mock_requests import *

user_analysis_request = {
    "spotify_access_info": spotify_access_info_sample
}


def test_get_user_analysis_success(mocker, client, env_patch):
    """
    Successful GET Playlists
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

    response = client.post('/api/user/analysis',
                           json=user_analysis_request
                           )
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
    Successful GET Playlists
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

    response = client.post('/api/user/analysis',
                           json=user_analysis_request
                           )
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["most_common_artists"] is not None
    assert response_json["most_common_albums"] is not None
    assert response_json["most_common_genre"] is not None
    assert response_json["total_length"] is not None
    assert response_json["average_track_length"] is not None
    # Number of playlists returned from spotify + one for Liked Tracks
    assert len(response_json["most_common_artists"]) == 0


def test_get_user_analysis_invalid_request_body_failure(mocker, client, env_patch):
    """
    Successful GET Playlists
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
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)
    mocker.patch.object(
        Spotify, "current_user_saved_tracks", return_value=mock_tracks_response)

    response = client.post('/api/user/analysis',
                           json={"request": "invalid request"}
                           )
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None
