import os
from tests import client
from unittest.mock import patch
from spotipy.oauth2 import SpotifyOAuth


@patch.dict(os.environ, {"SPOTIFY_CLIENT_ID": "1111111111111"})
@patch.dict(os.environ, {"SPOTIFY_CLIENT_SECRET": "222222222222"})
@patch.dict(os.environ, {"SPOTIFY_REDIRECT_URI": "http://localhost:3000"})
def test_get_spotify_uri_success(client):
    """
    Successful GET Spotify Uri
    """
    response = client.get('/api/spotify/auth/login')
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["loginUri"] is not None


@patch.dict(os.environ, {"SPOTIFY_CLIENT_ID": "1111111111111"})
@patch.dict(os.environ, {"SPOTIFY_CLIENT_SECRET": "222222222222"})
@patch.dict(os.environ, {"SPOTIFY_REDIRECT_URI": "http://localhost:3000"})
def test_handle_auth_code_success(mocker, client):
    """
    Successful POST Handle Auth Code
    """
    mocker.patch.object(SpotifyOAuth, "get_access_token",
                        return_value={
                            "access_token": "access token from spotify",
                            "refresh_token": "access token from spotify"
                        }
                        )
    response = client.post('/api/spotify/auth/code', json={"code": "1234"})
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["access_token"] is not None
    assert response_json["refresh_token"] is not None


@patch.dict(os.environ, {"SPOTIFY_CLIENT_ID": "1111111111111"})
@patch.dict(os.environ, {"SPOTIFY_CLIENT_SECRET": "222222222222"})
@patch.dict(os.environ, {"SPOTIFY_REDIRECT_URI": "http://localhost:3000"})
def test_handle_auth_code_failure_missing_code(mocker, client):
    """
    Failure POST Handle Auth Code
    Code missing
    """
    response = client.post('/api/spotify/auth/code')
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None


@patch.dict(os.environ, {"SPOTIFY_CLIENT_ID": "1111111111111"})
@patch.dict(os.environ, {"SPOTIFY_CLIENT_SECRET": "222222222222"})
@patch.dict(os.environ, {"SPOTIFY_REDIRECT_URI": "http://localhost:3000"})
def test_handle_auth_code_failure_upstream_spotify_error(mocker, client):
    """
    Failure POST Handle Auth Code
    Error from upstream Spotify
    """
    mocker.patch.object(SpotifyOAuth, "get_access_token",
                        return_value={
                            "error": "spotify error",
                        }
                        )
    response = client.post('/api/spotify/auth/code', json={"code": "1234"})
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None
