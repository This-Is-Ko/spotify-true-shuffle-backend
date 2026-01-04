from datetime import datetime, timezone

from database import database
from flask import current_app
from utils.constants import (
    PLAYLIST_COUNT_KEY, TRACK_COUNT_KEY, TRACKERS_ENABLED_KEY, OVERALL_COUNTER_KEY,
    USER_ID_KEY, RECENT_SHUFFLES_KEY, LAST_UPDATED_KEY,
    RECENT_SHUFFLES_PLAYLIST_ID_KEY, RECENT_SHUFFLES_TRACKS_SHUFFLED_KEY,
    RECENT_SHUFFLES_SHUFFLED_AT_KEY, RECENT_SHUFFLES_DURATION_SECONDS_KEY,
    RECENT_SHUFFLES_PLAYLIST_NAME_KEY, RECENT_SHUFFLES_CELERY_TASK_ID_KEY,
    RECENT_SHUFFLES_PLAYLIST_IMAGE_URL_KEY
)


MAX_RECENT_SHUFFLES = 10


def update_user_trackers(
        celery_task,
        user,
        playlist_id: str,
        playlist_name: str,
        track_count: int,
        duration_seconds: int,
        playlist_image_url: str = None
        ):
    if user is not None and track_count is not None:
        if user["user_attributes"][TRACKERS_ENABLED_KEY] is True:
            try:
                user_shuffle_counter = database.find_shuffle_counter(user[USER_ID_KEY])
                if user_shuffle_counter is None:
                    user_shuffle_counter = {
                        PLAYLIST_COUNT_KEY: 0,
                        TRACK_COUNT_KEY: 0,
                        RECENT_SHUFFLES_KEY: [],
                        LAST_UPDATED_KEY: datetime.now(timezone.utc)
                    }
                    current_app.logger.info("Creating shuffle history entry for user: " + user[USER_ID_KEY])

                user_shuffle_counter[PLAYLIST_COUNT_KEY] += 1
                user_shuffle_counter[TRACK_COUNT_KEY] += track_count

                user_shuffle_counter[LAST_UPDATED_KEY] = datetime.now(timezone.utc)

                celery_task_id = None
                if celery_task is not None and celery_task.request is not None:
                    celery_task_id = celery_task.request.id

                update_recent_shuffles(user_shuffle_counter,
                                       playlist_id,
                                       playlist_name,
                                       track_count,
                                       duration_seconds,
                                       celery_task_id,
                                       playlist_image_url)

                database.find_and_update_shuffle_counter(user[USER_ID_KEY], user_shuffle_counter)
            except Exception as e:
                current_app.logger.error("Error updating user shuffle count: " + str(e))


def update_recent_shuffles(
        user_shuffle_counter: dict,
        playlist_id: str,
        playlist_name: str,
        track_count: int,
        duration_seconds: int,
        celery_task_id: str,
        playlist_image_url: str = None
        ):
    if RECENT_SHUFFLES_KEY not in user_shuffle_counter:
        user_shuffle_counter[RECENT_SHUFFLES_KEY] = []

    # Append new shuffle entry
    new_recent_shuffles_entry = {
        RECENT_SHUFFLES_PLAYLIST_ID_KEY: playlist_id,
        RECENT_SHUFFLES_PLAYLIST_NAME_KEY: playlist_name,
        RECENT_SHUFFLES_TRACKS_SHUFFLED_KEY: track_count,
        RECENT_SHUFFLES_SHUFFLED_AT_KEY: datetime.now(timezone.utc),
        RECENT_SHUFFLES_DURATION_SECONDS_KEY: duration_seconds,
        RECENT_SHUFFLES_CELERY_TASK_ID_KEY: celery_task_id,
        RECENT_SHUFFLES_PLAYLIST_IMAGE_URL_KEY: playlist_image_url
    }
    user_shuffle_counter[RECENT_SHUFFLES_KEY].append(new_recent_shuffles_entry)

    # Keep only the last MAX_RECENT_SHUFFLES entries
    user_shuffle_counter[RECENT_SHUFFLES_KEY] = user_shuffle_counter[RECENT_SHUFFLES_KEY][-MAX_RECENT_SHUFFLES:]


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
