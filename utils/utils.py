import random
import spotipy
from datetime import date, datetime

from services.spotify_client import *
from schemas.Playlist import Playlist

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"


def get_tracks_from_playlist(spotify, playlist_id):
    """
    Get tracks from playlist based on playlist_id
    Use separate spotify call for retrieving Liked Tracks
    """
    offset = 0
    all_tracks = []
    if playlist_id == LIKED_TRACKS_PLAYLIST_ID:
        while True:
            tracks_response = spotify.current_user_saved_tracks(
                limit=50, offset=offset)
            if "items" in tracks_response:
                if len(tracks_response["items"]) == 0:
                    break
                for track in tracks_response["items"]:
                    all_tracks.append(track["track"]["uri"])
            offset += len(tracks_response["items"])
    else:
        while True:
            tracks_response = spotify.playlist_items(
                playlist_id, limit=50, offset=offset)
            if "items" in tracks_response:
                if len(tracks_response["items"]) == 0:
                    break
                for track in tracks_response["items"]:
                    all_tracks.append(track["track"]["uri"])
            offset += len(tracks_response["items"])
    return all_tracks


def get_liked_tracks_count(current_app, spotify):
    """
    Get number of songs in user library
    If error, return False"""
    liked_tracks_response = spotify.current_user_saved_tracks()
    get_liked_tracks_log = "Liked tracks response: {response}"
    # current_app.logger.debug(
    #     get_liked_tracks_log.format(response=liked_tracks_response))
    if "total" in liked_tracks_response:
        return liked_tracks_response["total"]
    return None


def create_new_playlist_with_tracks(current_app, spotify, new_playlist_name, public_status, playlist_description, tracks_to_add):
    try:
        # Create new playlist
        user_id = spotify.me()["id"]
        shuffled_playlist = spotify.user_playlist_create(
            user=user_id, name=new_playlist_name, public=public_status, description=playlist_description)

        # Add 100 tracks per call
        if len(tracks_to_add) <= 100:
            calls_required = 1
        else:
            calls_required = len(tracks_to_add) // 100 + 1
        left_over = len(tracks_to_add) % 100
        for i in range(calls_required):
            if i == calls_required - 1:
                add_items_response = spotify.playlist_add_items(
                    shuffled_playlist["id"], tracks_to_add[i*100: i*100+left_over])
            else:
                add_items_response = spotify.playlist_add_items(
                    shuffled_playlist["id"], tracks_to_add[i*100: i*100+100])
            if not "snapshot_id" in add_items_response:
                current_app.logger.error(
                    "Error while adding tracks. Response: " + add_items_response)
                return {
                    "error": "Unable to add tracks to playlist " + shuffled_playlist["id"]
                }
        create_playlist_with_tracks_success_log = "User: {user_id} -- Created playlist: {playlist_id} -- Length: {length:d}"
        current_app.logger.info(
            create_playlist_with_tracks_success_log.format(user_id=user_id, playlist_id=shuffled_playlist["id"], length=len(tracks_to_add)))
        return {
            "status": "success",
            "playlist_uri": shuffled_playlist["external_urls"]["spotify"],
            "num_of_tracks": len(tracks_to_add),
            "creation_time": datetime.now()
        }
    except Exception as e:
        current_app.logger.error(
            "Error while creating new playlist / adding tracks: " + str(e))
        return {
            "error": "Unable to create new playlist / add tracks to playlist "
        }
