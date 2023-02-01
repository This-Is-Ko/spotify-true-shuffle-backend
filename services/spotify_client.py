from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler

import os
from dotenv import load_dotenv
load_dotenv()


def create_auth_manager():
    return SpotifyOAuth(requests_session=False,
                        client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
                        client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
                        redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
                        scope="playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read")


def create_auth_manager_with_token(spotify_access_info):
    cache = MemoryCacheHandler(token_info=spotify_access_info)

    return SpotifyOAuth(requests_session=False,
                        client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
                        client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
                        redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
                        scope="playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read",
                        cache_handler=cache)
