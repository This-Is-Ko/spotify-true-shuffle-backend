from main import app
from flask import request

from services import spotify_playlist_service

@app.route('/api/spotify/me/playlists', methods=['POST'])
def get_playlists():
    data = request.get_json()
    if "spotifyAccessInfo" in data:
        return(spotify_playlist_service.get_user_playlists(data["spotifyAccessInfo"]))
    return {"error": "Missing spotify access token"}, 400