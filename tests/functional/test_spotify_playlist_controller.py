from tests import client, env_patch
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

from mock_responses import *

user_playlists_sample = {
    "items": [
        {
            "collaborative": True,
            "description": "string",
            "external_urls": {
                "spotify": "string"
            },
            "href": "string",
            "id": "string",
            "images": [
                {
                  "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n",
                  "height": 300,
                  "width": 300
                }
            ],
            "name": "string",
            "owner": {
                "external_urls": {
                    "spotify": "string"
                },
                "followers": {
                    "href": "string",
                    "total": 0
                },
                "href": "string",
                "id": "string",
                "type": "user",
                "uri": "string",
                "display_name": "string"
            },
            "public": True,
            "snapshot_id": "string",
            "tracks": {
                "href": "string",
                "total": 0
            },
            "type": "string",
            "uri": "string"
        }
    ],
    "href": "https://api.spotify.com/v1/me/shows?offset=0&limit=20\n",
    "limit": 20,
    "next": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
    "offset": 0,
    "previous": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
    "total": 1
}

spotify_access_info_sample = {
    "spotify_access_info": {
        "access_token": "spotify_access_token",
        "expires_at": 1668425997,
        "refresh_token": "spotify_refresh_token",
        "scope": "playlist-modify-private playlist-modify-public"
        + "playlist-read-collaborative playlist-read-private user-library-read",
        "token_type": "Bearer"
    }
}

mock_user_details_response = {
    "id": "user_id"
}


def test_get_playlists_success(mocker, client, env_patch):
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
    mocker.patch.object(Spotify, "current_user_playlists",
                        return_value=user_playlists_sample
                        )
    mocker.patch.object(
        Spotify, "me", return_value=mock_user_details_response)

    response = client.post('/api/playlist/me',
                           json=spotify_access_info_sample
                           )
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["all_playlists"] is not None
    # Number of playlists returned from spotify + one for Liked Tracks
    assert len(response_json["all_playlists"]) == 2


def test_get_playlists_failure_request_access_info_invalid(mocker, client, env_patch):
    """
    Failure GET Playlists
    Request access token structure invalid
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
                        return_value=user_playlists_sample
                        )
    response = client.post('/api/playlist/me',
                           json={"access token": "Invalid"}
                           )
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None


def test_get_playlists_failure_request_missing_body(mocker, client, env_patch):
    """
    Failure GET Playlists
    Request missing body
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
                        return_value=user_playlists_sample
                        )
    response = client.post('/api/playlist/me')
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None


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
    response = client.post('/api/playlist/me',
                           json=spotify_access_info_sample
                           )
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None
