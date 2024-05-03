import random
import spotipy
from datetime import date, datetime
from bson import json_util
import json
from flask import current_app
from tasks.task_state import get_celery_task_state
from database import database
from exceptions.custom_exceptions import SpotifyAuthInvalid
from services.spotify_client import *
from schemas.Playlist import Playlist
from tasks.playlist_tasks import create_playlist_from_liked_tracks, shuffle_playlist

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"


def get_user_playlists(spotify_auth: SpotifyAuth, include_stats):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth.to_dict()):
        raise SpotifyAuthInvalid("Invalid token")
    user = spotify.current_user()

    all_playlists = []
    # Add liked tracks as playlist option
    all_playlists.append(Playlist("Liked Tracks", user, LIKED_TRACKS_PLAYLIST_ID, {
                         "url": "https://misc.scdn.co/liked-songs/liked-songs-300.png"}))

    playlists = spotify.current_user_playlists()
    if playlists is not None and "items" in playlists:
        for playlist_entry in playlists["items"]:
            # Don't select playlists already shuffled
            if playlist_entry["name"].startswith(SHUFFLED_PLAYLIST_PREFIX):
                continue
            all_playlists.append(Playlist(
                playlist_entry["name"], playlist_entry["owner"], playlist_entry["id"], playlist_entry["images"][0]))

    get_playlists_success_log = "User: {user_id} -- Retrieved {num_of_playlists:d} playlists"
    current_app.logger.info(get_playlists_success_log.format(
        user_id=spotify.me()["id"], num_of_playlists=len(all_playlists)))

    response_body = dict()
    response_body["all_playlists"] = all_playlists

    # Include additional statistics if requested and enabled for user
    if include_stats is not None:
        if include_stats is True or include_stats.lower() == "true":
            user = database.find_user(user["id"])
            if user is not None and "user_attributes" in user and "trackers_enabled" in user["user_attributes"] and user["user_attributes"]["trackers_enabled"] == True:
                user_shuffle_counter = database.find_shuffle_counter(
                    user["user_id"])
                if user_shuffle_counter is not None:
                    response_body["user_shuffle_counter"] = json.loads(
                        json_util.dumps(user_shuffle_counter))
        # TODO Get overall stats
        # total_shuffle_counter = database.find_shuffle_counter("overall_counter")
        # response_body["user_shuffle_counter"] = json.loads(
        #     json_util.dumps(total_shuffle_counter))

    return response_body


def queue_create_shuffled_playlist(spotify_auth: SpotifyAuth, playlist_id, playlist_name):
    result = shuffle_playlist.delay(spotify_auth.to_dict(), playlist_id, playlist_name)
    current_app.logger.info("Shuffle id:" + result.id)
    return {"shuffle_task_id": result.id}


def get_shuffle_state(id: str):
    return get_celery_task_state(id, "Shuffle playlist")


def delete_all_shuffled_playlists(spotify_auth: SpotifyAuth):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth.to_dict()):
        raise SpotifyAuthInvalid("Invalid token")

    # Search all user playlists for shuffled playlists
    user_playlists = spotify.current_user_playlists()
    deleted_playlists = []
    for playlist in user_playlists["items"]:
        if str(playlist["name"]).startswith(SHUFFLED_PLAYLIST_PREFIX):
            spotify.current_user_unfollow_playlist(playlist["id"])
            deleted_playlists.append(playlist["id"])

    delete_success_log = "User: {user_id} -- Deleted {num_deleted_playlists:d} playlist(s): {deleted_playlists_list}"
    current_app.logger.info(delete_success_log.format(user_id=spotify.me()["id"], num_deleted_playlists=len(
        deleted_playlists), deleted_playlists_list=str(deleted_playlists)))
    return {
        "status": "success",
        "deleted_playlists_count": len(deleted_playlists)
    }


def queue_create_playlist_from_liked_tracks(spotify_auth: SpotifyAuth, new_playlist_name="My Liked Tracks"):
    result = create_playlist_from_liked_tracks.delay(spotify_auth.to_dict(), new_playlist_name)
    print("Create playlist id:" + result.id)
    return {"create_liked_playlist_id": result.id}


def get_create_playlist_from_liked_tracks_state(id: str):
    return get_celery_task_state(id, "Create liked playlist")
