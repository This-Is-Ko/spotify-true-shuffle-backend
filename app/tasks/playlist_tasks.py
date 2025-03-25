import time
from datetime import date
from typing import List
from celery import shared_task
import random
from flask import current_app

from database import database
from services.spotify_client import create_spotify_client
from utils import util, tracker_utils

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"


@shared_task(bind=True, ignore_result=False, expires=60)
def shuffle_playlist(self, spotify_auth_dict: dict, playlist_id, playlist_name):
    spotify_client = create_spotify_client(current_app, spotify_auth_dict)

    # Store start time to calculate duration
    start_time = time.time()

    # Grab all tracks from playlist
    all_tracks = util.get_tracks_from_playlist(self, spotify_client, playlist_id)
    if not all_tracks:
        return {"error": "No tracks found for playlist " + playlist_id}

    # Check if user exists
    user = database.find_user(spotify_client.me()["id"])
    if user is None:
        return {"error": "No user found"}

    util.update_task_progress(
        self,
        state='PROGRESS',
        meta={'progress': {'state': "Shuffling " + str(len(all_tracks)) + " tracks..."}}
    )
    random.shuffle(all_tracks)

    # Check if shuffled playlist exists and remove
    user_playlists = spotify_client.current_user_playlists()
    for playlist in user_playlists["items"]:
        if playlist["name"] == (SHUFFLED_PLAYLIST_PREFIX + playlist_name):
            spotify_client.current_user_unfollow_playlist(playlist["id"])
            break

    all_tracks_uri = [track['uri'] for track in all_tracks]

    response = util.create_new_playlist_with_tracks(
        self,
        spotify_client,
        SHUFFLED_PLAYLIST_PREFIX + playlist_name,
        False,
        "Shuffled by True Shuffle",
        all_tracks_uri
    )

    if response is not None and response["status"] == "success":
        # Queue celery task for updating track stats
        # update_track_statistics.delay(user[USER_ID_KEY], all_tracks)

        # Calculate duration of process
        duration_seconds = int(time.time() - start_time)

        # Increment user counters for playlists and tracks
        tracker_utils.update_user_trackers(self, user, playlist_id, playlist_name, len(all_tracks), duration_seconds)

        # Increment overall counters for playlists and tracks
        tracker_utils.update_overall_trackers(len(all_tracks))

    return response


@shared_task(bind=True, ignore_result=False, expires=60)
def create_playlist_from_liked_tracks(self, spotify_auth_dict: dict, new_playlist_name):
    spotify_client = create_spotify_client(current_app, spotify_auth_dict)

    all_tracks = util.get_tracks_from_playlist(self, spotify_client, LIKED_TRACKS_PLAYLIST_ID)
    if not all_tracks:
        return {"error": "No tracks found for user's liked songs"}

    today = date.today()

    all_tracks_uri = [track['uri'] for track in all_tracks]

    return util.create_new_playlist_with_tracks(
        self,
        spotify_client,
        new_playlist_name,
        True,
        "True Shuffle | My Liked Tracks from " + today.strftime("%d/%m/%Y"),
        all_tracks_uri
    )


@shared_task(bind=True, ignore_result=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def update_track_statistics(self, user_id: str, tracks: List[str]):
    """
    Updates database with track statistics.
    Increments shuffle counts or inserts new tracks if missing.
    """

    if not tracks or not user_id:
        return 0

    # Remove any tracks which are the user's local tracks
    filtered_tracks = [track for track in tracks if not track.get("is_local", False)]

    if not filtered_tracks:
        return 0

    database.update_track_statistics(filtered_tracks)
    num_tracks_updated = len(filtered_tracks)
    current_app.logger.info("User: " + user_id + "; Successfully stored tracks: " + str(num_tracks_updated))
    return num_tracks_updated
