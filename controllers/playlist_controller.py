from flask_cors import cross_origin
from marshmallow import ValidationError
from flask import current_app, request, Blueprint

from services import playlist_service
from schemas.ShufflePlaylistRequestSchema import ShufflePlaylistRequestSchema
from schemas.SpotifyAccessInfoRequestSchema import SpotifyAccessInfoRequestSchema
from schemas.ShareLikedTracksRequestSchema import ShareLikedTracksRequestSchema
from utils.utils import create_spotify_auth_object

playlist_controller = Blueprint(
    'playlist_controller', __name__, url_prefix='/api/playlist')


@playlist_controller.route('/me', methods=['GET'])
def get_playlists():
    try:
        spotify_auth = create_spotify_auth_object(request.cookies)
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        return (playlist_service.get_user_playlists(current_app, spotify_auth))
    except Exception as e:
        return {"error": "Unable to retrieve user playlists"}, 400


@playlist_controller.route('/shuffle', methods=['POST'])
def shuffle_playlist():
    try:
        spotify_auth = create_spotify_auth_object(request.cookies)

        request_data = request.get_json()
        schema = ShufflePlaylistRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        return (playlist_service.create_shuffled_playlist(current_app, spotify_auth, request_body["playlist_id"], request_body["playlist_name"]))
    except Exception as e:
        current_app.logger.info(
            "Unable to create shuffled playlist: " + str(e))
        return {"error": "Unable to create shuffled playlist"}, 400


@playlist_controller.route('/delete', methods=['DELETE'])
def delete_shuffled_playlists():
    try:
        spotify_auth = create_spotify_auth_object(request.cookies)
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        return (playlist_service.delete_all_shuffled_playlists(current_app, spotify_auth))
    except Exception as e:
        current_app.logger.info(
            "Unable to delete shuffled playlists: " + str(e))
        return {"error": "Unable to delete shuffled playlists"}, 400


@playlist_controller.route('/share/liked-tracks', methods=['POST'])
def liked_tracks_to_playlist():
    try:
        spotify_auth = create_spotify_auth_object(request.cookies)

        request_data = request.get_json()
        schema = ShareLikedTracksRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        if ("playlist_name" in request_body):
            return (playlist_service.create_playlist_from_liked_tracks(current_app, spotify_auth, request_body["playlist_name"]))
        else:
            return (playlist_service.create_playlist_from_liked_tracks(current_app, spotify_auth))
    except Exception as e:
        current_app.logger.info(
            "Unable to create share playlist: " + str(e))
        return {"error": "Unable to create share playlist"}, 400
