from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
from spotipy import Spotify
from dotenv import load_dotenv
from classes.spotify_auth import SpotifyAuth

load_dotenv()


def create_auth_manager(current_app):
    return SpotifyOAuth(requests_session=False,
                        client_id=current_app.config["SPOTIFY_CLIENT_ID"],
                        client_secret=current_app.config["SPOTIFY_CLIENT_SECRET"],
                        redirect_uri=current_app.config["SPOTIFY_REDIRECT_URI"],
                        scope=(
                            "playlist-modify-private playlist-modify-public playlist-read-private"
                            + "playlist-read-collaborative user-library-read"
                        ))


def create_auth_manager_with_token(current_app, spotify_auth: SpotifyAuth):
    return create_auth_manager_with_token_dict(current_app, spotify_auth.to_dict())


def create_auth_manager_with_token_dict(current_app, spotify_auth_dict: dict):
    cache = MemoryCacheHandler(token_info=spotify_auth_dict)

    return SpotifyOAuth(requests_session=False,
                        client_id=current_app.config["SPOTIFY_CLIENT_ID"],
                        client_secret=current_app.config["SPOTIFY_CLIENT_SECRET"],
                        redirect_uri=current_app.config["SPOTIFY_REDIRECT_URI"],
                        scope=(
                            "playlist-modify-private playlist-modify-public playlist-read-private"
                            + "playlist-read-collaborative user-library-read"
                        ),
                        cache_handler=cache)


def create_spotify_client(current_app, spotify_auth_dict) -> Spotify:
    auth_manager = create_auth_manager_with_token_dict(current_app, spotify_auth_dict)
    return Spotify(auth_manager=auth_manager)
