from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler

from dotenv import load_dotenv

from classes.spotify_auth import SpotifyAuth
load_dotenv()


def create_auth_manager(current_app):
    return SpotifyOAuth(requests_session=False,
                        client_id=current_app.config["SPOTIFY_CLIENT_ID"],
                        client_secret=current_app.config["SPOTIFY_CLIENT_SECRET"],
                        redirect_uri=current_app.config["SPOTIFY_REDIRECT_URI"],
                        scope="playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read")


def create_auth_manager_with_token(current_app, spotify_auth: SpotifyAuth):
    cache = MemoryCacheHandler(token_info=spotify_auth.to_dict())

    return SpotifyOAuth(requests_session=False,
                        client_id=current_app.config["SPOTIFY_CLIENT_ID"],
                        client_secret=current_app.config["SPOTIFY_CLIENT_SECRET"],
                        redirect_uri=current_app.config["SPOTIFY_REDIRECT_URI"],
                        scope="playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read",
                        cache_handler=cache)
