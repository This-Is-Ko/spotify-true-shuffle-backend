import spotipy
from bson import json_util
import json
from flask import current_app
from tasks.task_state import get_celery_task_state
from database import database
from exceptions.custom_exceptions import GetPlaylistsException, InvalidUser, SpotifyAuthInvalid
from classes.spotify_auth import SpotifyAuth
from services.spotify_client import create_auth_manager_with_token
from schemas.Playlist import Playlist
from tasks import playlist_tasks
from utils.logger_utils import logErrorWithUser, logInfoWithUser

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"


def get_user_playlists(spotify_auth: SpotifyAuth, include_stats):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth.to_dict()):
        raise SpotifyAuthInvalid("Invalid token")
    user = spotify.me()
    if user is None or user["id"] is None:
        raise InvalidUser("User not found in Spotify")
    user_id = user["id"]

    all_playlists = []
    # Add liked tracks as playlist option
    all_playlists.append(Playlist("Liked Tracks", user, LIKED_TRACKS_PLAYLIST_ID, {
                         "url": "https://misc.scdn.co/liked-songs/liked-songs-300.png"}, None))
    logInfoWithUser("Added Liked Tracks playlist", spotify_auth)

    # Retrieve user's playlists and parse details
    try:
        playlists = spotify.current_user_playlists(limit=50)
        if playlists is None or "total" not in playlists or "items" not in playlists:
            raise GetPlaylistsException("Failed to retrieve user's playlists")

        if playlists["total"] < 1:
            logInfoWithUser("No playlists found for user", spotify_auth)
        else:
            logInfoWithUser(f"User has {playlists['total']} playlists", spotify_auth)
            for playlist_entry in playlists["items"]:
                # Skip playlists missing info
                if playlist_entry is None or "name" not in playlist_entry:
                    logInfoWithUser(f"Missing playlist name for playlist", spotify_auth)
                    continue
                playlist_name = playlist_entry["name"]
                #Validate id is present
                if "id" not in playlist_entry:
                    logInfoWithUser(f"Missing playlist id for playlist: {playlist_name}", spotify_auth)
                    continue
                playlist_id = playlist_entry["id"]
                # Validate track info is present
                tracks_info = playlist_entry.get("tracks")
                if not tracks_info or "total" not in tracks_info:
                    logInfoWithUser(f"Missing track info for playlist: {playlist_name} (id: {playlist_id})", spotify_auth)
                    continue
                # Skip playlists which are shuffled previously based on prefixed name
                if playlist_name.startswith(SHUFFLED_PLAYLIST_PREFIX):
                    continue
                # Validate playlist owner and id info is present
                if "owner" not in playlist_entry:
                    logInfoWithUser(f"Missing playlist owner for playlist: {playlist_name} (id: {playlist_id})", spotify_auth)
                    continue
                # Validate playlist images are present
                images = playlist_entry.get("images", [])
                if not images:
                    logInfoWithUser(f"Missing playlist images for playlist: {playlist_name} (id: {playlist_id})", spotify_auth)
                    continue
                playlist_owner = playlist_entry["owner"]
                playlist_image = images[0]
                num_of_tracks = tracks_info["total"]
                all_playlists.append(Playlist(
                    playlist_name,
                    playlist_owner,
                    playlist_id,
                    playlist_image,
                    num_of_tracks
                ))
    except Exception as e:
        # Handle playlist logging error
        try:
            logErrorWithUser(f"Get current user playlists - Playlist response: {json.dumps(playlists, default=str)}", spotify_auth)
        except TypeError as ex:
            logErrorWithUser(f"Get current user playlists - Error serializing playlists: {ex}", spotify_auth)
        raise GetPlaylistsException(f"Failed to parse Spotify playlists: {e}")
    logInfoWithUser(f"Retrieved {len(all_playlists):d} playlists", spotify_auth)

    response_body = dict()
    response_body["all_playlists"] = all_playlists

    # Include additional statistics if requested and enabled for user
    if include_stats is not None:
        if include_stats is True or include_stats.lower() == "true":
            user = database.find_user(user_id)
            if (
                user is not None and "user_attributes" in user
                and "trackers_enabled" in user["user_attributes"]
                and user["user_attributes"]["trackers_enabled"] is True
            ):
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
    result = playlist_tasks.shuffle_playlist.delay(spotify_auth.to_dict(), playlist_id, playlist_name)
    if result is None:
        logErrorWithUser(f"Shuffle queue failed", spotify_auth)
        return None
    logInfoWithUser(f"Shuffle id: {result.id}", spotify_auth)
    return {"shuffle_task_id": result.id}


def get_shuffle_state(spotify_auth: SpotifyAuth, id: str):
    return get_celery_task_state(spotify_auth, id, "Shuffle playlist")


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

    logInfoWithUser(f"Deleted {len(deleted_playlists):d} playlist(s): {str(deleted_playlists)}", spotify_auth)
    return {
        "status": "success",
        "deleted_playlists_count": len(deleted_playlists)
    }


def queue_create_playlist_from_liked_tracks(spotify_auth: SpotifyAuth, new_playlist_name="My Liked Tracks"):
    result = playlist_tasks.create_playlist_from_liked_tracks.delay(spotify_auth.to_dict(), new_playlist_name)
    print("Create playlist id:" + result.id)
    return {"create_liked_playlist_id": result.id}


def get_create_playlist_from_liked_tracks_state(spotify_auth: SpotifyAuth, id: str):
    return get_celery_task_state(spotify_auth, id, "Create liked playlist")
