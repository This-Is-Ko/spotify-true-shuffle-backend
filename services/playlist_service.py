import random
import spotipy
from datetime import date, datetime

# from database import database
from services.spotify_client import *
from schemas.Playlist import Playlist

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"


def get_user_playlists(current_app, spotify_auth):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth):
        return {"error": "Invalid token"}, 400
    user = spotify.current_user()

    playlists = spotify.current_user_playlists()
    if not "items" in playlists:
        return {"error": "Unable to retrieve playlists"}, 400

    all_playlists = []
    # Add liked tracks as playlist option
    all_playlists.append(Playlist("Liked Tracks", user, LIKED_TRACKS_PLAYLIST_ID, {
                         "url": "https://misc.scdn.co/liked-songs/liked-songs-300.png"}))
    for playlist_entry in playlists["items"]:
        # Don't select playlists already shuffled
        if playlist_entry["name"].startswith(SHUFFLED_PLAYLIST_PREFIX):
            continue
        all_playlists.append(Playlist(
            playlist_entry["name"], playlist_entry["owner"], playlist_entry["id"], playlist_entry["images"][0]))

    get_playlists_success_log = "User: {user_id} -- Retrieved {num_of_playlists:d} playlists"
    current_app.logger.info(get_playlists_success_log.format(
        user_id=spotify.me()["id"], num_of_playlists=len(all_playlists)))
    return {"all_playlists": all_playlists}


def create_shuffled_playlist(current_app, spotify_auth, playlist_id, playlist_name):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth):
        return {"error": "Invalid token"}, 400

    # Grab all tracks from playlist
    all_tracks = get_tracks_from_playlist(spotify, playlist_id)

    if len(all_tracks) == 0:
        return {"error": "No tracks found for playlist " + playlist_id}

    # TODO Check if user exists and shuffle tracker settings
    # user = database.find_user(spotify.me()["id"])
    # if user is not None:
    #     if user[TRACK_SHUFFLES_ATTRIBUTE_NAME] is True:

    try:
        # Increment counters for playlists and tracks
        with open(current_app.config["COUNTER_DIRECTORY"] + '/playlist_counter.txt', 'r') as f:
            t = f.read()
        with open(current_app.config["COUNTER_DIRECTORY"] + '/playlist_counter.txt', 'w') as f:
            f.write(str(int(t)+1))

        with open(current_app.config["COUNTER_DIRECTORY"] + '/track_counter.txt', 'r') as f:
            t = f.read()
        with open(current_app.config["COUNTER_DIRECTORY"] + '/track_counter.txt', 'w') as f:
            f.write(str(int(t)+len(all_tracks)))
    except Exception as e:
        current_app.logger.error("Error updating trackers: " + str(e))

    random.shuffle(all_tracks)

    # Check if shuffled playlist exists and remove
    user_playlists = spotify.current_user_playlists()
    for playlist in user_playlists["items"]:
        if playlist["name"] == (SHUFFLED_PLAYLIST_PREFIX + playlist_name):
            spotify.current_user_unfollow_playlist(playlist["id"])
            break

    return create_new_playlist_with_tracks(current_app, spotify, SHUFFLED_PLAYLIST_PREFIX + playlist_name, False, "Shuffled by True Shuffle", all_tracks)


def delete_all_shuffled_playlists(current_app, spotify_auth):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth):
        return {"error": "Invalid token"}, 400

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
    liked_tracks = spotify.current_user_saved_tracks()
    get_liked_tracks_log = "Liked tracks response: {response}"
    current_app.logger.debug(
        get_liked_tracks_log.format(response=liked_tracks))
    return liked_tracks["total"]


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


def create_playlist_from_liked_tracks(current_app, spotify_auth, new_playlist_name):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth):
        return {"error": "Invalid token"}, 400

    all_tracks = get_tracks_from_playlist(spotify, LIKED_TRACKS_PLAYLIST_ID)

    today = date.today()

    return create_new_playlist_with_tracks(current_app, spotify, new_playlist_name, True, "My Liked Tracks from " + today.strftime("%d/%m/%Y"), all_tracks)
