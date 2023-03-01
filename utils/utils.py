import random
import spotipy
from datetime import date, datetime

from services.spotify_client import *
from schemas.Playlist import Playlist

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"


def get_all_tracks_with_data_from_playlist(spotify, playlist_id):
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
                    all_tracks.append(track)
            offset += len(tracks_response["items"])
            if offset >= tracks_response["total"]:
                break
    else:
        while True:
            tracks_response = spotify.playlist_items(
                playlist_id, limit=50, offset=offset)
            if "items" in tracks_response:
                if len(tracks_response["items"]) == 0:
                    break
                for track in tracks_response["items"]:
                    all_tracks.append(track)
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
