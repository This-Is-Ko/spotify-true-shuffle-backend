from database import database
import spotipy
from bson import json_util
import json

from services.spotify_client import *

TRACK_LIKED_TRACKS_ATTRIBUTE_NAME = "track_liked_tracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"


def save_user(current_app, spotify_access_info, user_attributes):
    """
    Check if user exists and update
    Otherwise create new user entry
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user_entry = {
        "spotify": {
            "expires_at": spotify_access_info["expires_at"],
            "refresh_token": spotify_access_info["refresh_token"],
            "scope": spotify_access_info["scope"]
        },
        "user_attributes": user_attributes
    }
    user = database.find_and_update_user(
        user_id, user_entry)

    user_json = json.loads(json_util.dumps(user))
    if (user != None):
        return {
            "status": "success",
            "user": user_json
        }
    return {
        "status": "error"
    }


def get_user(current_app, spotify_access_info):
    """
    Check if user exists and update
    Otherwise create new user entry
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user = database.find_user(user_id)

    user_json = json.loads(json_util.dumps(user))
    if (user != None):
        return {
            "user": user_json
        }
    return {
        "status": "error"
    }, 400


def get_user_tracker_data(current_app, spotify_access_info, tracker_name):
    """
    Check if tracker enabled for user
    If enabled, retrieve all data points for user
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user = database.find_user(user_id)

    user_json = json.loads(json_util.dumps(user))

    # Check tracker status
    if (tracker_name not in user_json["user_attributes"] or user_json["user_attributes"][tracker_name] is not True):
        return {
            "status": "error",
            "message": "Tracker not enabled"
        }, 400

    try:
        # Get all tracker data points
        if (tracker_name == TRACK_LIKED_TRACKS_ATTRIBUTE_NAME):
            data_cursor = database.get_all_user_liked_tracks_history_data(
                user_id)
        elif (tracker_name == TRACK_SHUFFLES_ATTRIBUTE_NAME):
            data_cursor = database.get_all_user_shuffles_history_data(
                user_id)
        else:
            return {
                "status": "error",
                "message": "track_name invalid"
            }, 400
        data = json.loads(json_util.dumps(list(data_cursor)))
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        return {
            "status": "error"
        }, 400
