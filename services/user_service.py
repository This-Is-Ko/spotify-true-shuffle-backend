from database import database
import spotipy
from bson import json_util
import json

from services.spotify_client import *


def save_user(current_app, spotify_access_info, user_settings):
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
    user = database.find_and_update_user(user_id, user_settings)

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
