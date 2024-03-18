from datetime import datetime
from flask import current_app

from services.spotify_client import *
from schemas.Playlist import Playlist

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"


def get_tracks_from_playlist(task, spotify, playlist_id):
    """
    Get tracks from playlist based on playlist_id
    Use separate spotify call for retrieving Liked Tracks
    """
    offset = 0
    all_tracks = []
    while True:
        if playlist_id == LIKED_TRACKS_PLAYLIST_ID:
            tracks_response = spotify.current_user_saved_tracks(
                limit=50, offset=offset)
        else:
            tracks_response = spotify.playlist_items(
                playlist_id, limit=50, offset=offset)
        if tracks_response != None and "items" in tracks_response:
            if len(tracks_response["items"]) == 0:
                break
            for track in tracks_response["items"]:
                all_tracks.append(track["track"]["uri"])
        offset += len(tracks_response["items"])
        task.update_state(state='PROGRESS', meta={'progress': {'state': "Retrieved " + str(len(all_tracks)) + " tracks so far..."}})
    return all_tracks


def get_all_tracks_with_data_from_playlist(task, spotify, playlist_id):
    """
    Get tracks from playlist based on playlist_id
    Use separate spotify call for retrieving Liked Tracks
    """
    offset = 0
    all_tracks = []
    while True:
        if playlist_id == LIKED_TRACKS_PLAYLIST_ID:
            tracks_response = spotify.current_user_saved_tracks(limit=50, offset=offset)
        else:
            tracks_response = spotify.playlist_items(playlist_id, limit=50, offset=offset)
        if "items" in tracks_response:
            if len(tracks_response["items"]) == 0:
                break
            for track in tracks_response["items"]:
                all_tracks.append(track)
        offset += len(tracks_response["items"])
        task.update_state(state='PROGRESS', meta={'progress': {'state': "Retrieved " + str(len(all_tracks)) + " tracks so far..."}})
        if offset >= tracks_response["total"]:
            break
    return all_tracks


def get_liked_tracks_count(current_app, spotify):
    """
    Get number of songs in user library
    If error, return False
    """
    liked_tracks_response = spotify.current_user_saved_tracks()
    get_liked_tracks_log = "Liked tracks response: {response}"
    # current_app.logger.debug(
    #     get_liked_tracks_log.format(response=liked_tracks_response))
    if "total" in liked_tracks_response:
        return liked_tracks_response["total"]
    return None


def get_all_track_audio_features(task, current_app, spotify, tracks):
    """
    Get audio features for all tracks
    If error, return False
    """
    task.update_state(state='PROGRESS', meta={'progress': {'state': "Getting audio features for each track"}})
    tracks_left = len(tracks)
    index = 0
    all_track_features = []
    while tracks_left > 0:
        # Max 100 tracks at once
        if tracks_left < 100:
            tracks_to_analyse = tracks[index: index + tracks_left]
            tracks_left -= tracks_left
            index += tracks_left
        else:
            tracks_to_analyse = tracks[index: index + 100]
            tracks_left -= 100
            index += 100
        response = spotify.audio_features(tracks_to_analyse)
        all_track_features += response
        task.update_state(state='PROGRESS', meta={'progress': {'state': "Retrieved audio features for " + str(index) + " tracks so far..."}})
    return all_track_features


def calcFromMillis(milliseconds):
    seconds = (milliseconds/1000) % 60
    seconds = int(seconds)
    minutes = (milliseconds/(1000*60)) % 60
    minutes = int(minutes)
    hours = (milliseconds/(1000*60*60)) % 24
    hours = int(hours)
    days = (milliseconds/(1000*60*60*24)) % 365
    days = int(days)
    return seconds, minutes, hours, days


def create_new_playlist_with_tracks(task, spotify, new_playlist_name, public_status, playlist_description, tracks_to_add):
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
                task.update_state(state='PROGRESS', meta={'progress': {'state': "Adding  " + str(i*100+left_over) + "/" + str(len(tracks_to_add)) + " tracks..."}})
            else:
                add_items_response = spotify.playlist_add_items(
                    shuffled_playlist["id"], tracks_to_add[i*100: i*100+100])
                task.update_state(state='PROGRESS', meta={'progress': {'state': "Added " + str(i*100+100) + "/" + str(len(tracks_to_add)) + " tracks"}})
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