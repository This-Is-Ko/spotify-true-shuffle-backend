import random

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from services.spotify_client import *
from schemas.Playlist import Playlist

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"

def create_shuffled_playlist(spotify_access_info, playlist_id, playlist_name):
    auth_manager = create_auth_manager()
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    
    # Grab all tracks from playlist
    offset = 0
    all_tracks = []
    if playlist_id == LIKED_TRACKS_PLAYLIST_ID:
        while True:
            tracks_response = spotify.current_user_saved_tracks(limit=50, offset=offset)
            if "items" in tracks_response:
                if len(tracks_response["items"]) == 0:
                    break
                for track in tracks_response["items"]:
                    all_tracks.append(track["track"]["uri"])
            offset += len(tracks_response["items"])
    else:
        while True:
            tracks_response = spotify.playlist_tracks(playlist_id, limit=50, offset=offset)
            if "items" in tracks_response:
                if len(tracks_response["items"]) == 0:
                    break
                for track in tracks_response["items"]:
                    all_tracks.append(track["track"]["uri"])
            offset += len(tracks_response["items"])
    
    if len(all_tracks) == 0:
        return {"error": "No tracks found for playlist " + playlist_id}

    random.shuffle(all_tracks)
    
    # Check if shuffled playlist exists and remove
    
    # Create new playlist
    user_id = spotify.me()["id"]
    shuffled_playlist = spotify.user_playlist_create(user=user_id, name=SHUFFLED_PLAYLIST_PREFIX + playlist_name, description="Shuffled by True Shuffle")
    
    # Add 100 tracks per call
    if len(all_tracks) <= 100:
        calls_required = 1
    else:
        calls_required = len(all_tracks) // 100
    left_over = len(all_tracks) % 100
    for i in range(calls_required):
        if i == calls_required - 1:
            print(spotify.playlist_add_items(shuffled_playlist["id"], all_tracks[i*100: left_over]))
        else:
            print(spotify.playlist_add_items(shuffled_playlist["id"], all_tracks[i*100: i*100+100]))
    
    return {"shuffled_playlist": shuffled_playlist}
