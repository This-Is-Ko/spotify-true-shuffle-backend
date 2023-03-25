from tests import client, env_patch
from spotipy.oauth2 import SpotifyOAuth


def test_get_spotify_uri_success(client, env_patch):
    """
    Successful GET Spotify Uri
    """
    response = client.get('/api/spotify/auth/login')
    response_json = response.get_json()
    assert response.status_code == 200
    assert response_json["loginUri"] is not None


def test_handle_auth_code_success(mocker, client, env_patch):
    """
    Successful POST Handle Auth Code
    """
    mocker.patch.object(SpotifyOAuth, "get_access_token",
                        return_value={
                            "access_token": "accesstokenfromspotify",
                            "refresh_token": "refreshtokenfromspotify",
                            "expires_at": 12345,
                            "scope": "scopefromspotify"
                        }
                        )
    response = client.post('/api/spotify/auth/code', json={"code": "1234"})
    assert response.status_code == 200
    assert response.headers['Set-Cookie'] is not None

    expected_cookies = [
        'trueshuffle-spotifyAccessToken=accesstokenfromspotify',
        'trueshuffle-spotifyRefreshToken=refreshtokenfromspotify',
        'trueshuffle-spotifyExpiresAt=12345',
        'trueshuffle-spotifyScope=scopefromspotify']
    success_count = 0
    for expected in expected_cookies:
        for header in response.headers:
            if expected in header[1]:
                success_count += 1
                break

    assert success_count == 4


def test_handle_auth_code_failure_missing_code(mocker, client, env_patch):
    """
    Failure POST Handle Auth Code
    Code missing
    """
    response = client.post('/api/spotify/auth/code')
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json["error"] is not None


def test_handle_auth_code_failure_upstream_spotify_error(mocker, client, env_patch):
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
