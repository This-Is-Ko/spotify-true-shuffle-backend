from flask_cors import cross_origin
from marshmallow import ValidationError
from flask import current_app, request, Blueprint, make_response
from exceptions.custom_exceptions import SessionExpired, SessionIdNone, SessionIdNotFound

from services import playlist_service
from schemas.ShufflePlaylistRequestSchema import ShufflePlaylistRequestSchema
from schemas.ShareLikedTracksRequestSchema import ShareLikedTracksRequestSchema
from utils.auth_utils import extend_session_expiry
from decorators.spotify_auth_validator import spotify_auth_validator
from decorators.schema_validator import validate_request_schema

playlist_controller = Blueprint('playlist_controller', __name__, url_prefix='/api/playlist')


@playlist_controller.route('/me', methods=['GET'])
@spotify_auth_validator
def get_playlists(spotify_auth):
    include_stats= False
    if request.args != None:
        include_stats = request.args.get("include-stats")

    try:
        response = make_response(playlist_service.get_user_playlists(spotify_auth, include_stats))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error("Unable to retrieve user playlists: " + str(e))
        if spotify_auth is not None and spotify_auth.user_id is not None:
            current_app.logger.error("User: " + spotify_auth.user_id)
        return {"error": "Unable to retrieve user playlists"}, 400


@playlist_controller.route('/shuffle', methods=['POST'])
@spotify_auth_validator
@validate_request_schema(ShufflePlaylistRequestSchema)
def queue_shuffle_playlist(spotify_auth, request_body):
    try:
        response = make_response(playlist_service.queue_create_shuffled_playlist(
            spotify_auth, request_body["playlist_id"], request_body["playlist_name"]))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to queue to create shuffled playlist: " + str(e))
        return {"error": "Unable to queue to create shuffled playlist"}, 400
    

@playlist_controller.route('/shuffle/state/<id>', methods=['GET'])
@spotify_auth_validator
def get_shuffle_state(id):
    try:
        response = make_response(playlist_service.get_shuffle_state(id))
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to retrieve shuffle state: " + str(e))
        return {"error": "Unable to retrieve shuffle state"}, 400


@playlist_controller.route('/delete', methods=['DELETE'])
@spotify_auth_validator
def delete_shuffled_playlists(spotify_auth):
    try:
        response = make_response(playlist_service.delete_all_shuffled_playlists(spotify_auth))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to delete shuffled playlists: " + str(e))
        return {"error": "Unable to delete shuffled playlists"}, 400


@playlist_controller.route('/share/liked-tracks', methods=['POST'])
@spotify_auth_validator
@validate_request_schema(ShareLikedTracksRequestSchema)
def liked_tracks_to_playlist(spotify_auth, request_body):

    try:
        if "playlist_name" in request_body and request_body["playlist_name"] != "":
            response = make_response(playlist_service.queue_create_playlist_from_liked_tracks(spotify_auth, request_body["playlist_name"]))
            extend_session_expiry(response, request.cookies)
            return response
        else:
            response = make_response(playlist_service.queue_create_playlist_from_liked_tracks(spotify_auth))
            extend_session_expiry(response, request.cookies)
            return response
    except Exception as e:
        current_app.logger.error(
            "Unable to create share playlist: " + str(e))
        return {"error": "Unable to create share playlist"}, 400


@playlist_controller.route('/share/liked-tracks/<id>', methods=['GET'])
@spotify_auth_validator
def get_liked_tracks_to_playlist_state(id):
    try:
        response = make_response(playlist_service.get_create_playlist_from_liked_tracks_state(id))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to get create liked playlist state: " + str(e))
        return {"error": "Unable to get create liked playlist state"}, 400
