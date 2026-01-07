from classes.spotify_auth import SpotifyAuth
from tasks.analysis_tasks import aggregate_user_data, get_user_analysis, get_user_tracker_data
from database import database
import spotipy
from bson import json_util
import json

from flask import current_app, g
from exceptions.custom_exceptions import SpotifyAuthInvalid
from services.spotify_client import create_auth_manager_with_token
from tasks.task_state import get_celery_task_state
from utils.constants import RECENT_SHUFFLES_KEY

LIKED_TRACKS_PLAYLIST_ID = "likedTracks"

TRACKERS_ENABLED_ATTRIBUTE_NAME = "trackers_enabled"
TRACK_LIKED_TRACKS_ATTRIBUTE_NAME = "track_liked_tracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"
ANALYSE_LIBRARY_ATTRIBUTE_NAME = "analyse_library"


def save_user(spotify_auth: SpotifyAuth, user_attributes):
    """
    Check if user exists and update
    Otherwise create new user entry
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth.to_dict()):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user_entry = {
        "spotify": {
            "expires_at": spotify_auth.expires_at,
            "refresh_token": spotify_auth.refresh_token,
            "scope": spotify_auth.scope
        },
        "user_attributes": user_attributes
    }
    user = database.find_and_update_user(
        user_id, user_entry)

    user_json = json.loads(json_util.dumps(user))
    if (user is not None):
        return {
            "status": "success",
            "user": user_json
        }
    return {
        "status": "error"
    }, 400


def get_user(spotify_auth: SpotifyAuth):
    """
    Check if user exists and update
    Otherwise create new user entry
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth.to_dict()):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user = database.find_user(user_id)

    user_json = json.loads(json_util.dumps(user))
    if (user is not None):
        return {
            "user": user_json
        }
    return {
        "status": "error"
    }, 400


def queue_get_aggregate_user_data(spotify_auth: SpotifyAuth):
    """
    Return celery task id
    """
    correlation_id = g.correlation_id if hasattr(g, 'correlation_id') else None
    result = aggregate_user_data.delay(spotify_auth.to_dict(), correlation_id)
    print("Aggregate data id:" + result.id)
    return {"aggregate_task_id": result.id}


def get_aggregate_user_data_state(spotify_auth: SpotifyAuth, id: str):
    return get_celery_task_state(spotify_auth, id, "Aggregate user data")


def handle_get_user_tracker_data(spotify_auth: SpotifyAuth, tracker_name):
    """
    Check if trackers are enabled for user
    If enabled, retrieve all data points for user
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth.to_dict()):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user = database.find_user(user_id)
    user_json = json.loads(json_util.dumps(user))
    try:
        return get_user_tracker_data(user_id, user_json, tracker_name)
    except Exception as e:
        current_app.logger.error("Error in handle_get_user_tracker_data: " + str(e))
        return {
            "status": "error"
        }, 400


def handle_get_user_analysis(spotify_auth: SpotifyAuth):
    """
    Get all liked tracks to analyse
    Calcuate most common tracks/artists/genres
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth.to_dict()):
        return {"error": "Invalid token"}, 400
    try:
        correlation_id = g.correlation_id if hasattr(g, 'correlation_id') else None
        # Note: get_user_analysis expects a task object, but we're calling it directly
        # Passing None for task since this is not a Celery task context
        return get_user_analysis(None, current_app, spotify, correlation_id)
    except Exception as e:
        current_app.logger.error("Error in handle_get_user_analysis: " + str(e))
        return {
            "status": "error"
        }, 400


def get_recent_shuffles(spotify_auth: SpotifyAuth):
    """
    Retrieve recent shuffle history for the authenticated user.
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth.to_dict()):
        raise SpotifyAuthInvalid("Invalid token")
    user = spotify.me()
    if user is None:
        raise Exception("User not found in Spotify")

    user_shuffle_counter_entry = database.find_shuffle_counter(user["id"])

    if user_shuffle_counter_entry is not None and user_shuffle_counter_entry[RECENT_SHUFFLES_KEY] is not None:
        recent_shuffles = user_shuffle_counter_entry[RECENT_SHUFFLES_KEY]
        return {
          "recent_shuffles": json.loads(json_util.dumps(recent_shuffles))
        }
    else:
        return {"recent_shuffles": []}
