
from flask import current_app, request, Blueprint

from services import spotify_playlist_service

spotify_playlist_controller = Blueprint(
    'spotify_playlist_controller', __name__, url_prefix='/api/spotify/me')


@spotify_playlist_controller.route('/playlists', methods=['POST'])
def get_playlists():
    try:
        data = request.get_json()
        if "spotifyAccessInfo" in data:
            data["spotifyAccessInfo"]["expires_at"] = int(
                data["spotifyAccessInfo"]["expires_at"])
            return (spotify_playlist_service.get_user_playlists(current_app, data["spotifyAccessInfo"]))
        return {"error": "Missing spotify access token"}, 400
    except Exception as e:
        return {"error": "Unable to retrieve user playlists"}, 400
