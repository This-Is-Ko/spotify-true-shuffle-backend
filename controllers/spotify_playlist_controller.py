
from flask import current_app, request, Blueprint
from marshmallow import ValidationError

from services import spotify_playlist_service
from schemas.SpotifyAccessInfoRequestSchema import SpotifyAccessInfoRequestSchema

spotify_playlist_controller = Blueprint(
    'spotify_playlist_controller', __name__, url_prefix='/api/spotify/me')


@spotify_playlist_controller.route('/playlists', methods=['POST'])
def get_playlists():
    try:
        request_data = request.get_json()
        schema = SpotifyAccessInfoRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        return (spotify_playlist_service.get_user_playlists(current_app, request_body["spotify_access_info"]))
    except Exception as e:
        return {"error": "Unable to retrieve user playlists"}, 400
