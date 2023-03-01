import time

spotify_access_info_sample = {
    "token_type": "Bearer",
    "access_token": "access token from spotify",
    "refresh_token": "access token from spotify",
    "expires_at": int(time.time()) + 3600,
    "scope": "playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read"
}
