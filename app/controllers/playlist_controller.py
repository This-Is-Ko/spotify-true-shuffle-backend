from flask_cors import cross_origin
from marshmallow import ValidationError
from flask import current_app, request, Blueprint, make_response
from exceptions.custom_exceptions import SessionExpired, SessionIdNone, SessionIdNotFound

from services import playlist_service
from schemas.ShufflePlaylistRequestSchema import ShufflePlaylistRequestSchema
from schemas.ShareLikedTracksRequestSchema import ShareLikedTracksRequestSchema
from utils.auth_utils import extend_session_expiry, validate_session

playlist_controller = Blueprint(
    'playlist_controller', __name__, url_prefix='/api/playlist')


@playlist_controller.route('/me', methods=['GET'])
def get_playlists():
    try:
        spotify_auth = validate_session(request.cookies)
        include_stats = request.args.get("include-stats")

    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        response = make_response(playlist_service.get_user_playlists(
            current_app, spotify_auth, include_stats))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error("Unable to retrieve user playlists" + str(e))
        return {"error": "Unable to retrieve user playlists"}, 400


@playlist_controller.route('/shuffle', methods=['POST'])
def queue_shuffle_playlist():
    try:
        spotify_auth = validate_session(request.cookies)

        request_data = request.get_json()
        schema = ShufflePlaylistRequestSchema()
        request_body = schema.load(request_data)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except ValidationError as e:
        current_app.logger.error("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

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
def get_shuffle_state(id):
    try:
        validate_session(request.cookies)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400
    
    try:
        response = make_response(playlist_service.get_shuffle_state(id))
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to retrieve shuffle state: " + str(e))
        return {"error": "Unable to retrieve shuffle state"}, 400


@playlist_controller.route('/delete', methods=['DELETE'])
def delete_shuffled_playlists():
    try:
        spotify_auth = validate_session(request.cookies)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        response = make_response(
            playlist_service.delete_all_shuffled_playlists(current_app, spotify_auth))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to delete shuffled playlists: " + str(e))
        return {"error": "Unable to delete shuffled playlists"}, 400


@playlist_controller.route('/share/liked-tracks', methods=['POST'])
def liked_tracks_to_playlist():
    try:
        spotify_auth = validate_session(request.cookies)

        request_data = request.get_json()
        schema = ShareLikedTracksRequestSchema()
        request_body = schema.load(request_data)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except ValidationError as e:
        current_app.logger.error("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

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
def get_liked_tracks_to_playlist_state(id):
    try:
        validate_session(request.cookies)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        response = make_response(playlist_service.get_create_playlist_from_liked_tracks_state(id))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to get create liked playlist state: " + str(e))
        return {"error": "Unable to get create liked playlist state"}, 400
