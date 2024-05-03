from datetime import date
from celery import shared_task
import random
import spotipy
import time
from flask import current_app

from classes.spotify_auth import SpotifyAuth
from database import database
from services.spotify_client import create_auth_manager_with_token
from utils.util import create_new_playlist_with_tracks, get_tracks_from_playlist


SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"

@shared_task(bind=True, ignore_result=False, expires=60)
def shuffle_playlist(self, spotify_auth: SpotifyAuth, playlist_id, playlist_name):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    # Grab all tracks from playlist
    all_tracks = get_tracks_from_playlist(self, spotify, playlist_id)

    if len(all_tracks) == 0:
        return {"error": "No tracks found for playlist " + playlist_id}

    # Check if user exists and shuffle tracker settings
    user = database.find_user(spotify.me()["id"])

    # Increment user counters for playlists and tracks
    if user is not None:
        if user["user_attributes"]["trackers_enabled"] is True:
            try:
                user_shuffle_counter = database.find_shuffle_counter(
                    user["user_id"])
                if user_shuffle_counter == None:
                    user_shuffle_counter = dict()
                    user_shuffle_counter["playlist_count"] = 0
                    user_shuffle_counter["track_count"] = 0
                    current_app.logger.info(
                        "Creating shuffle history entry for user: " + user["user_id"])

                user_shuffle_counter["playlist_count"] = int(
                    user_shuffle_counter["playlist_count"]) + 1
                user_shuffle_counter["track_count"] = int(
                    user_shuffle_counter["track_count"]) + len(all_tracks)

                user_shuffle_counter_update = database.find_and_update_shuffle_counter(
                    user["user_id"],
                    user_shuffle_counter)
            except Exception as e:
                current_app.logger.error(
                    "Error updating user shuffle count: " + str(e))

    # Increment overall counters for playlists and tracks
    try:
        total_shuffle_counter = database.find_shuffle_counter(
            "overall_counter")
        if total_shuffle_counter == None:
            raise Exception("Couldn't find total shuffle counter")

        total_shuffle_counter["playlist_count"] = int(
            total_shuffle_counter["playlist_count"]) + 1
        total_shuffle_counter["track_count"] = int(
            total_shuffle_counter["track_count"]) + len(all_tracks)

        total_shuffle_counter_update = database.find_and_update_shuffle_counter(
            "overall_counter",
            total_shuffle_counter)
    except Exception as e:
        current_app.logger.error(
            "Error updating overall shuffle count: " + str(e))
        
    random.shuffle(all_tracks)
    self.update_state(state='PROGRESS', meta={'progress': {'state': "Shuffling " + str(len(all_tracks)) + " tracks"}})

    # Check if shuffled playlist exists and remove
    user_playlists = spotify.current_user_playlists()
    for playlist in user_playlists["items"]:
        if playlist["name"] == (SHUFFLED_PLAYLIST_PREFIX + playlist_name):
            spotify.current_user_unfollow_playlist(playlist["id"])
            break

    return create_new_playlist_with_tracks(self, spotify, SHUFFLED_PLAYLIST_PREFIX + playlist_name, False, "Shuffled by True Shuffle", all_tracks)


@shared_task(bind=True, ignore_result=False, expires=60)
def create_playlist_from_liked_tracks(self, spotify_auth: SpotifyAuth, new_playlist_name):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    # if not auth_manager.validate_token(spotify_auth.to_dict()):
    #     raise SpotifyAuthInvalid("Invalid token")

    all_tracks = get_tracks_from_playlist(self, spotify, LIKED_TRACKS_PLAYLIST_ID)

    today = date.today()

    return create_new_playlist_with_tracks(self, spotify, new_playlist_name, True, "True Shuffle | My Liked Tracks from " + today.strftime("%d/%m/%Y"), all_tracks)