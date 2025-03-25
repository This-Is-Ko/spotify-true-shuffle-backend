from flask_cors import cross_origin  # noqa: F401
from flask import current_app, request, Blueprint, make_response

from services import playlist_service
from schemas.ShufflePlaylistRequestSchema import ShufflePlaylistRequestSchema
from schemas.ShareLikedTracksRequestSchema import ShareLikedTracksRequestSchema
from utils.auth_utils import extend_session_expiry
from decorators.spotify_auth_validator import spotify_auth_validator
from decorators.schema_validator import request_schema_validator

playlist_controller = Blueprint('playlist_controller', __name__, url_prefix='/api/playlist')


@playlist_controller.route('/me', methods=['GET'])
@spotify_auth_validator
def get_playlists(spotify_auth):
    """
    Endpoint to retrieve user playlists
    Validate Spotify authentication and optionally includes playlist statistics
    """
    include_stats = False
    if request.args is not None:
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
@request_schema_validator(ShufflePlaylistRequestSchema)
def queue_shuffle_playlist(spotify_auth, request_body):
    """
    Endpoint to queue the creation of a shuffled playlist
    Validates Spotify authentication and request body schema
    """
    try:
        response = make_response(playlist_service.queue_create_shuffled_playlist(
            spotify_auth, request_body["playlist_id"], request_body["playlist_name"]))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error("Unable to queue to create shuffled playlist: " + str(e))
        return {"error": "Unable to queue to create shuffled playlist"}, 400


@playlist_controller.route('/shuffle/state/<id>', methods=['GET'])
@spotify_auth_validator
def get_shuffle_state(id, spotify_auth):
    """
    Endpoint to get the state of a shuffled playlist creation process
    Validates Spotify authentication
    """
    try:
        response = make_response(playlist_service.get_shuffle_state(id))
        return response
    except Exception as e:
        current_app.logger.error("Unable to retrieve shuffle state: " + str(e))
        return {"error": "Unable to retrieve shuffle state"}, 400


@playlist_controller.route('/delete', methods=['DELETE'])
@spotify_auth_validator
def delete_shuffled_playlists(spotify_auth):
    """
    Endpoint to delete all shuffled playlists for the authenticated user
    Validates Spotify authentication
    """
    try:
        response = make_response(playlist_service.delete_all_shuffled_playlists(spotify_auth))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error("Unable to delete shuffled playlists: " + str(e))
        return {"error": "Unable to delete shuffled playlists"}, 400


@playlist_controller.route('/share/liked-tracks', methods=['POST'])
@spotify_auth_validator
@request_schema_validator(ShareLikedTracksRequestSchema)
def liked_tracks_to_playlist(spotify_auth, request_body):
    """
    Endpoint to queue the creation of a playlist from liked tracks
    Validates Spotify authentication and request body schema
    """
    try:
        if "playlist_name" in request_body and request_body["playlist_name"] != "":
            response = make_response(
                playlist_service.queue_create_playlist_from_liked_tracks(spotify_auth, request_body["playlist_name"])
            )
            extend_session_expiry(response, request.cookies)
            return response
        else:
            response = make_response(playlist_service.queue_create_playlist_from_liked_tracks(spotify_auth))
            extend_session_expiry(response, request.cookies)
            return response
    except Exception as e:
        current_app.logger.error("Unable to create share playlist: " + str(e))
        return {"error": "Unable to create share playlist"}, 400


@playlist_controller.route('/share/liked-tracks/<id>', methods=['GET'])
@spotify_auth_validator
def get_liked_tracks_to_playlist_state(id, spotify_auth):
    """
    Endpoint to retrieve the state of a playlist creation from liked tracks
    Validates Spotify authentication
    """
    try:
        response = make_response(playlist_service.get_create_playlist_from_liked_tracks_state(spotify_auth, id))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error("Unable to get create liked playlist state: " + str(e))
        return {"error": "Unable to get create liked playlist state"}, 400
