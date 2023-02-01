import random
import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from services.spotify_client import *
from schemas.Playlist import Playlist

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"


def create_shuffled_playlist(spotify_access_info, playlist_id, playlist_name):
    auth_manager = create_auth_manager_with_token(spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400

    # Grab all tracks from playlist
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
            tracks_response = spotify.playlist_tracks(
                playlist_id, limit=50, offset=offset)
            if "items" in tracks_response:
                if len(tracks_response["items"]) == 0:
                    break
                for track in tracks_response["items"]:
                    all_tracks.append(track["track"]["uri"])
            offset += len(tracks_response["items"])

    if len(all_tracks) == 0:
        return {"error": "No tracks found for playlist " + playlist_id}

    # Increment counters for playlists and tracks
    with open(os.environ.get("COUNTER_DIRECTORY") + '/playlist_counter.txt', 'r') as f:
        t = f.read()
    with open(os.environ.get("COUNTER_DIRECTORY") + '/playlist_counter.txt', 'w') as f:
        f.write(str(int(t)+1))

    with open(os.environ.get("COUNTER_DIRECTORY") + '/track_counter.txt', 'r') as f:
        t = f.read()
    with open(os.environ.get("COUNTER_DIRECTORY") + '/track_counter.txt', 'w') as f:
        f.write(str(int(t)+len(all_tracks)))

    random.shuffle(all_tracks)

    # Check if shuffled playlist exists and remove
    user_playlists = spotify.current_user_playlists()
    for playlist in user_playlists["items"]:
        if playlist["name"] == (SHUFFLED_PLAYLIST_PREFIX + playlist_name):
            spotify.current_user_unfollow_playlist(playlist["id"])
            break

    # Create new playlist
    user_id = spotify.me()["id"]
    shuffled_playlist = spotify.user_playlist_create(
        user=user_id, name=SHUFFLED_PLAYLIST_PREFIX + playlist_name, public=False, description="Shuffled by True Shuffle")

    # Add 100 tracks per call
    if len(all_tracks) <= 100:
        calls_required = 1
    else:
        calls_required = len(all_tracks) // 100 + 1
    left_over = len(all_tracks) % 100
    for i in range(calls_required):
        if i == calls_required - 1:
            add_items_response = spotify.playlist_add_items(
                shuffled_playlist["id"], all_tracks[i*100: i*100+left_over])
        else:
            add_items_response = spotify.playlist_add_items(
                shuffled_playlist["id"], all_tracks[i*100: i*100+100])
        if not "snapshot_id" in add_items_response:
            return {
                "error": "Unable to add tracks to playlist " + playlist_id
            }

    return {
        "status": "success",
        "playlistUri": shuffled_playlist["external_urls"]["spotify"]
    }


def delete_all_shuffled_playlists(spotify_access_info):
    auth_manager = create_auth_manager_with_token(spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400

    deleted_playlists_count = 0
    # Search all user playlists for shuffled playlists
    user_playlists = spotify.current_user_playlists()
    for playlist in user_playlists["items"]:
        if str(playlist["name"]).startswith(SHUFFLED_PLAYLIST_PREFIX):
            spotify.current_user_unfollow_playlist(playlist["id"])
            deleted_playlists_count += 1

    return {
        "status": "success",
        "deletedPlaylistsCount": deleted_playlists_count
    }
