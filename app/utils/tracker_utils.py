from database import database
from flask import current_app

def update_user_trackers(user, track_count: int):
    if user is not None and track_count is not None:
        if user["user_attributes"]["trackers_enabled"] is True:
            try:
                user_shuffle_counter = database.find_shuffle_counter(user["user_id"])
                if user_shuffle_counter == None:
                    user_shuffle_counter = dict()
                    user_shuffle_counter["playlist_count"] = 0
                    user_shuffle_counter["track_count"] = 0
                    current_app.logger.info("Creating shuffle history entry for user: " + user["user_id"])

                user_shuffle_counter["playlist_count"] = int(
                    user_shuffle_counter["playlist_count"]) + 1
                user_shuffle_counter["track_count"] = int(
                    user_shuffle_counter["track_count"]) + track_count

                database.find_and_update_shuffle_counter(user["user_id"], user_shuffle_counter)
            except Exception as e:
                current_app.logger.error("Error updating user shuffle count: " + str(e))
                
def update_overall_trackers(track_count: int):
    if track_count is not None:
        try:
            total_shuffle_counter = database.find_shuffle_counter("overall_counter")
            if total_shuffle_counter == None:
                raise Exception("Couldn't find total shuffle counter")

            total_shuffle_counter["playlist_count"] = int(total_shuffle_counter["playlist_count"]) + 1
            total_shuffle_counter["track_count"] = int(total_shuffle_counter["track_count"]) + track_count

            database.find_and_update_shuffle_counter("overall_counter", total_shuffle_counter)
        except Exception as e:
            current_app.logger.error("Error updating overall shuffle count: " + str(e))