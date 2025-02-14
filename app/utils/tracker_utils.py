from database import database
from flask import current_app
from utils.constants import PLAYLIST_COUNT_KEY, TRACK_COUNT_KEY, TRACKERS_ENABLED_KEY, OVERALL_COUNTER_KEY, USER_ID_KEY


def update_user_trackers(user, track_count: int):
    if user is not None and track_count is not None:
        if user["user_attributes"][TRACKERS_ENABLED_KEY] is True:
            try:
                user_shuffle_counter = database.find_shuffle_counter(user[USER_ID_KEY])
                if user_shuffle_counter is None:
                    user_shuffle_counter = dict()
                    user_shuffle_counter[PLAYLIST_COUNT_KEY] = 0
                    user_shuffle_counter[TRACK_COUNT_KEY] = 0
                    current_app.logger.info("Creating shuffle history entry for user: " + user[USER_ID_KEY])

                user_shuffle_counter[PLAYLIST_COUNT_KEY] = int(user_shuffle_counter[PLAYLIST_COUNT_KEY]) + 1
                user_shuffle_counter[TRACK_COUNT_KEY] = int(user_shuffle_counter[TRACK_COUNT_KEY]) + track_count

                database.find_and_update_shuffle_counter(user[USER_ID_KEY], user_shuffle_counter)
            except Exception as e:
                current_app.logger.error("Error updating user shuffle count: " + str(e))


def update_overall_trackers(track_count: int):
    if track_count is not None:
        try:
            total_shuffle_counter = database.find_shuffle_counter(OVERALL_COUNTER_KEY)
            if total_shuffle_counter is None:
                raise Exception("Couldn't find total shuffle counter")

            total_shuffle_counter[PLAYLIST_COUNT_KEY] = int(total_shuffle_counter[PLAYLIST_COUNT_KEY]) + 1
            total_shuffle_counter[TRACK_COUNT_KEY] = int(total_shuffle_counter[TRACK_COUNT_KEY]) + track_count

            database.find_and_update_shuffle_counter(OVERALL_COUNTER_KEY, total_shuffle_counter)
        except Exception as e:
            current_app.logger.error("Error updating overall shuffle count: " + str(e))
