import spotipy
import datetime
import time

from database import database
from services.spotify_client import create_auth_manager_with_token
from utils import util
from utils.constants import USER_ID_KEY

TRACKERS_ENABLED_ATTRIBUTE_NAME = "trackers_enabled"
TRACK_LIKED_TRACKS_ATTRIBUTE_NAME = "track_liked_tracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"
USER_LIKED_TRACKS_TRACKER_LOG = "Tracker: {tracker} -- User: {user_id} -- {status}"
SUCCESSFUL_UPDATES_LOG = (
    "Tracker: {tracker} -- Successfully updated {success_counter} users"
    + "out of {total_enabled_users} users"
)


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
        time.sleep(2)
        total_users += 1
        if is_user_entry_valid(user) is False:
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user[USER_ID_KEY] if USER_ID_KEY in user else "missing id",
                           "Failed to update due to invalid user entry",
                           level="error")
            continue
        auth_manager = create_auth_manager_with_token(
            current_app, user["spotify"])
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        # Force refresh_token
        if not auth_manager.validate_token(user["spotify"]) or not auth_manager.refresh_access_token(
                user["spotify"]["refresh_token"]):
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user[USER_ID_KEY], "Failed to validate user token", level="error")
            continue
        current_count = util.get_liked_tracks_count(spotify)
        if current_count is None:
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user[USER_ID_KEY], "Failed to get new liked tracks count", level="error")
            continue

        # Find previous user entry if exists to calculate difference
        # For a new user, first entry difference will be 0
        difference = 0
        try:
            previous_entry = database.find_user_latest_liked_tracks_history_entry(
                user[USER_ID_KEY])
            if previous_entry is not None:
                difference = current_count - previous_entry["count"]
        except Exception as e:
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user[USER_ID_KEY],
                           "Error while searching for previous tracker entry" + str(e),
                           level="error")
            continue

        tracker_entry = {
            USER_ID_KEY: user[USER_ID_KEY],
            "count": current_count,
            "difference": difference,
            "created": datetime.datetime.today()
        }

        try:
            database.insert_liked_tracks_history_entry(
                tracker_entry)
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user[USER_ID_KEY], "Successfully added new tracker entry")
            success_counter += 1
        except Exception as e:
            tracker_logger(current_app, USER_LIKED_TRACKS_TRACKER_LOG, TRACK_SHUFFLES_ATTRIBUTE_NAME,
                           user[USER_ID_KEY], "Error while added new tracker entry" + str(e), level="error")
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
    if (
        USER_ID_KEY not in user or "user_attributes" not in user
        or TRACKERS_ENABLED_ATTRIBUTE_NAME not in user["user_attributes"] or "spotify" not in user
    ):
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
