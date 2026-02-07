import time
from datetime import date
from typing import List
from celery import shared_task
import random
from flask import current_app

from database import database
from services.spotify_client import create_spotify_client
from utils import util, tracker_utils
from utils.logger_utils import logWarning, logInfo
from classes.shuffle_type import Shuffle_Type

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"


@shared_task(bind=True, ignore_result=False, expires=60)
def shuffle_playlist(self, spotify_auth_dict: dict, playlist_id, playlist_name, correlation_id=None, 
        shuffle_type: str = Shuffle_Type.CLASSIC_NEW_PLAYLIST.value
    ):
    # Store correlation_id in task metadata and request context for logging
    if correlation_id:
        self.update_state(state='PROGRESS', meta={'correlation_id': correlation_id})
        # Store in request context for logger_utils access
        if not hasattr(self.request, 'meta'):
            self.request.meta = {}
        self.request.meta['correlation_id'] = correlation_id
    
    spotify_client = create_spotify_client(current_app, spotify_auth_dict)

    # Store start time to calculate duration
    start_time = time.time()

    # Fetch playlist details to get image URL
    playlist_image_url = None
    if playlist_id == LIKED_TRACKS_PLAYLIST_ID:
        # Use default liked songs image URL
        playlist_image_url = "https://misc.scdn.co/liked-songs/liked-songs-300.png"
    else:
        try:
            playlist_details = spotify_client.playlist(playlist_id)
            if playlist_details and "images" in playlist_details and len(playlist_details["images"]) > 0:
                playlist_image_url = playlist_details["images"][0].get("url")
        except Exception as e:
            logWarning(f"Could not fetch playlist image for {playlist_id}: {str(e)}")

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
        meta={'progress': {'state': "Shuffling " + str(len(all_tracks)) + " tracks..."}},
        correlation_id=correlation_id
    )
    random.shuffle(all_tracks)

    # Check if shuffled playlist exists
    user_playlists = spotify_client.current_user_playlists()
    shuffled_playlist_id = None
    for playlist in user_playlists["items"]:
        if playlist["name"] == (SHUFFLED_PLAYLIST_PREFIX + playlist_name):
            shuffled_playlist_id = playlist["id"]
            shuffled_playlist_uri = playlist["external_urls"]["spotify"]
            break

    all_tracks_uri = [track['uri'] for track in all_tracks]

    response = None
    if shuffle_type == Shuffle_Type.REUSE_EXISTING_PLAYLIST.value and shuffled_playlist_id:
        # Reuse existing shuffled playlist if selected and exists
        response = util.reuse_existing_playlist_with_updated_tracks(
            self,
            spotify_client,
            shuffled_playlist_id,
            shuffled_playlist_uri,
            all_tracks_uri
        )
    else:
        # Classic: create new playlist
        # Clean up existing shuffled playlist
        if shuffled_playlist_id != None:
            spotify_client.current_user_unfollow_playlist(shuffled_playlist_id)

        response = util.create_new_playlist_with_tracks(
            self,
            spotify_client,
            SHUFFLED_PLAYLIST_PREFIX + playlist_name,
            False,
            "Shuffled by True Shuffle",
            all_tracks_uri
        )

    if response is not None and response["status"] == "success":
        # Calculate duration of process
        duration_seconds = int(time.time() - start_time)

        # Increment user counters for playlists and tracks
        tracker_utils.update_user_trackers(self, user, playlist_id, playlist_name, len(all_tracks), duration_seconds, playlist_image_url)

        # Increment overall counters for playlists and tracks
        tracker_utils.update_overall_trackers(len(all_tracks))

    return response


@shared_task(bind=True, ignore_result=False, expires=60)
def create_playlist_from_liked_tracks(self, spotify_auth_dict: dict, new_playlist_name, correlation_id=None):
    # Store correlation_id in task metadata and request context for logging
    if correlation_id:
        self.update_state(state='PROGRESS', meta={'correlation_id': correlation_id})
        # Store in request context for logger_utils access
        if not hasattr(self.request, 'meta'):
            self.request.meta = {}
        self.request.meta['correlation_id'] = correlation_id
    
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
def update_track_statistics(self, user_id: str, tracks: List[str], correlation_id=None):
    """
    Updates database with track statistics.
    Increments shuffle counts or inserts new tracks if missing.
    """
    # Store correlation_id in task metadata and request context for logging
    if correlation_id:
        self.update_state(state='PROGRESS', meta={'correlation_id': correlation_id})
        # Store in request context for logger_utils access
        if not hasattr(self.request, 'meta'):
            self.request.meta = {}
        self.request.meta['correlation_id'] = correlation_id

    if not tracks or not user_id:
        return 0

    # Remove any tracks which are the user's local tracks
    filtered_tracks = [track for track in tracks if not track.get("is_local", False)]

    if not filtered_tracks:
        return 0

    database.update_track_statistics(filtered_tracks)
    num_tracks_updated = len(filtered_tracks)
    logInfo("User: " + user_id + "; Successfully stored tracks: " + str(num_tracks_updated))
    return num_tracks_updated
