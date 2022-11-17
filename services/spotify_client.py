import spotipy
from spotipy.oauth2 import SpotifyOAuth

import os
from dotenv import load_dotenv
load_dotenv()

def create_auth_manager():
    return SpotifyOAuth( requests_session=False,
        client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
        client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
        scope="playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read")