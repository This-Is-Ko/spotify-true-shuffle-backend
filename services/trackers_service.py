import spotipy
import datetime

from database import database
from services.spotify_client import *
from utils import utils

TRACKERS_ENABLED_ATTRIBUTE_NAME = "trackers_enabled"
TRACK_LIKED_TRACKS_ATTRIBUTE_NAME = "track_liked_tracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"
USER_LIKED_TRACKS_TRACKER_LOG = "Tracker: {tracker} -- User: {user_id} -- {status}"
SUCCESSFUL_UPDATES_LOG = "Tracker: {tracker} -- Successfully updated {success_counter} users out of {total_enabled_users} users"


def update_trackers(current_app):
    """
    For each user who has tracker enabled, check latest liked tracks count and store.
    Skip users who error
    """
    users = database.get_all_users_with_attribute(
        TRACKERS_ENABLED_ATTRIBUTE_NAME, True)
    success_counter = 0
    # Track total users as users object is cursor
    total_users = 0
    for user in users:
        total_users += 1
        if is_user_entry_valid(user) == False:
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user["user_id"] if "user_id" in user else "missing id", "Failed to update due to invalid user entry", level="error")
            continue
        auth_manager = create_auth_manager_with_token(
            current_app, user["spotify"])
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        # Force refresh_token
        if not auth_manager.validate_token(user["spotify"]) or not auth_manager.refresh_access_token(
                user["spotify"]["refresh_token"]):
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user["user_id"], "Failed to validate user token", level="error")
            continue
        current_count = utils.get_liked_tracks_count(current_app, spotify)
        if current_count is None:
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user["user_id"], "Failed to get new liked tracks count", level="error")
            continue

        # Find previous user entry if exists to calculate difference
        # For a new user, first entry difference will be 0
        difference = 0
        try:
            previous_entry = database.find_user_latest_liked_tracks_history_entry(
                user["user_id"])
            if previous_entry is not None:
                difference = current_count - previous_entry["count"]
        except Exception as e:
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user["user_id"], "Error while searching for previous tracker entry" + str(e), level="error")
            continue

        tracker_entry = {
            "user_id": user["user_id"], "count": current_count, "difference": difference, "created": datetime.datetime.today()}

        try:
            insert_result = database.insert_liked_tracks_history_entry(
                tracker_entry)
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user["user_id"], "Successfully added new tracker entry")
            success_counter += 1
        except Exception as e:
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user["user_id"], "Error while added new tracker entry" + str(e), level="error")
            continue
    current_app.logger.info(SUCCESSFUL_UPDATES_LOG.format(
        tracker=TRACK_SHUFFLES_ATTRIBUTE_NAME, success_counter=success_counter, total_enabled_users=total_users))
    return {
        "status": "success",
        "message": "Finished updating trackers",
        "updated_users": success_counter,
        "total_enabled_users": total_users
    }


def is_user_entry_valid(user):
    if "user_id" not in user or "user_attributes" not in user or TRACKERS_ENABLED_ATTRIBUTE_NAME not in user["user_attributes"] or "spotify" not in user:
        return False

    # required values for spotipy to use refresh token
    if "refresh_token" not in user["spotify"] or "expires_at" not in user["spotify"] or "scope" not in user["spotify"]:
        return False

    return True


def tracker_logger(current_app, log_string, tracker_name, user_id, status_message, level="info"):
    if level == "info":
        current_app.logger.info(log_string.format(
            tracker=tracker_name, user_id=user_id, status=status_message))
    elif level == "error":
        current_app.logger.error(log_string.format(
            tracker=tracker_name, user_id=user_id, status=status_message))
