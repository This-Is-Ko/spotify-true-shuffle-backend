from database import database
import spotipy
from bson import json_util
import json

from services.spotify_client import *
from utils.utils import *

LIKED_TRACKS_PLAYLIST_ID = "likedTracks"

TRACK_LIKED_TRACKS_ATTRIBUTE_NAME = "track_liked_tracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"
ANALYSE_LIBRARY_ATTRIBUTE_NAME = "analyse_library"


def save_user(current_app, spotify_access_info, user_attributes):
    """
    Check if user exists and update
    Otherwise create new user entry
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user_entry = {
        "spotify": {
            "expires_at": spotify_access_info["expires_at"],
            "refresh_token": spotify_access_info["refresh_token"],
            "scope": spotify_access_info["scope"]
        },
        "user_attributes": user_attributes
    }
    user = database.find_and_update_user(
        user_id, user_entry)

    user_json = json.loads(json_util.dumps(user))
    if (user != None):
        return {
            "status": "success",
            "user": user_json
        }
    return {
        "status": "error"
    }


def get_user(current_app, spotify_access_info):
    """
    Check if user exists and update
    Otherwise create new user entry
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user = database.find_user(user_id)

    user_json = json.loads(json_util.dumps(user))
    if (user != None):
        return {
            "user": user_json
        }
    return {
        "status": "error"
    }, 400


def get_user_tracker_data(current_app, spotify_access_info, tracker_name):
    """
    Check if tracker enabled for user
    If enabled, retrieve all data points for user
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user = database.find_user(user_id)

    user_json = json.loads(json_util.dumps(user))

    # Check tracker status
    if (tracker_name not in user_json["user_attributes"] or user_json["user_attributes"][tracker_name] is not True):
        return {
            "status": "error",
            "message": "Tracker not enabled"
        }, 400

    try:
        # Get all tracker data points
        if (tracker_name == TRACK_LIKED_TRACKS_ATTRIBUTE_NAME):
            data_cursor = database.get_all_user_liked_tracks_history_data(
                user_id)
        elif (tracker_name == TRACK_SHUFFLES_ATTRIBUTE_NAME):
            data_cursor = database.get_all_user_shuffles_history_data(
                user_id)
        else:
            return {
                "status": "error",
                "message": "track_name invalid"
            }, 400
        data = json.loads(json_util.dumps(list(data_cursor)))
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        return {
            "status": "error"
        }, 400


def get_user_analysis(current_app, spotify_access_info):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user = database.find_user(user_id)

    user_json = json.loads(json_util.dumps(user))

    # TODO Check ANALYSE_LIBRARY_ATTRIBUTE_NAME status
    # if (ANALYSE_LIBRARY_ATTRIBUTE_NAME not in user_json["user_attributes"] or user_json["user_attributes"][ANALYSE_LIBRARY_ATTRIBUTE_NAME] is not True):
    #     return {
    #         "status": "error",
    #         "message": "Tracker not enabled"
    #     }, 400

    try:
        # Get all tracks from library
        all_tracks = get_all_tracks_with_data_from_playlist(
            spotify, LIKED_TRACKS_PLAYLIST_ID)

        most_common_artists = {}
        most_common_albums = {}
        most_common_genre = {}
        total_length = 0
        average_track_length = 0
        oldest_release_date_track = ""
        for track in all_tracks:
            track_data = track["track"]
            current_app.logger.debug(
                "Adding track data for: " + track_data["name"])
            # Most common artist
            for artist in track_data["artists"]:
                if artist["name"] in most_common_artists:
                    most_common_artists[artist["name"]]["count"] += 1
                else:
                    artist_image_url = ""
                    if "images" in artist:
                        artist_image_url = artist["images"][0]["url"]
                    most_common_artists[artist["name"]] = {
                        "id": artist["id"],
                        "name": artist["name"],
                        "external_url": artist["external_urls"]["spotify"],
                        "image": artist_image_url,
                        "count": 1
                    }
            # Most common album
            album = track_data["album"]
            if album["name"] in most_common_albums:
                most_common_albums[album["name"]]["count"] += 1
            else:
                album_image_url = ""
                if "images" in artist:
                    album_image_url = album["images"][0]["url"]
                most_common_albums[album["name"]] = {
                    "id": album["id"],
                    "name": album["name"],
                    "external_url": album["external_urls"]["spotify"],
                    "image": album_image_url,
                    "count": 1
                }
            # Most common genre
            if "genres" in album:
                for genre in album["genres"]:
                    if genre in most_common_genre:
                        most_common_genre[genre] += 1
                    else:
                        most_common_genre[genre] = 1
            # Average track length
            total_length += int(track_data["duration_ms"])

        average_track_length = total_length / len(all_tracks)
        average_track_length_seconds, average_track_length_minutes, average_track_length_hours, average_track_length_days = calcFromMillis(
            average_track_length)
        total_length_seconds, total_length_minutes, total_length_hours, total_length_days = calcFromMillis(
            total_length)
        # average_track_length_seconds = (average_track_length/1000) % 60
        # average_track_length_seconds = int(average_track_length_seconds)
        # average_track_length_minutes = (average_track_length/(1000*60)) % 60
        # average_track_length_minutes = int(average_track_length_minutes)
        # average_track_length_hours = (average_track_length/(1000*60*60)) % 24

        # TODO Get top items from spotify (require scope extension)
        # all_time_top_artists = spotify.current_user_top_artists(
        #     limit=50, time_range="long_term")["items"]
        # all_time_top_tracks = spotify.current_user_top_tracks(
        #     limit=50, time_range="long_term")["items"]

        most_common_artists_array = []
        for v in most_common_artists.values():
            most_common_artists_array.append(v)
        most_common_albums_array = []
        for v in most_common_albums.values():
            most_common_albums_array.append(v)
        most_common_genre_array = []
        for k, v in most_common_genre.items():
            most_common_genre_array.append({"name": k, "count": v})

        return {
            "most_common_artists": most_common_artists_array,
            "most_common_albums": most_common_albums_array,
            "most_common_genre": most_common_genre_array,
            "total_length": {
                "days": total_length_days,
                "hours": total_length_hours,
                "minutes": total_length_minutes,
                "seconds": total_length_seconds,
            },
            "average_track_length": {
                "days": average_track_length_days,
                "hours": average_track_length_hours,
                "minutes": average_track_length_minutes,
                "seconds": average_track_length_seconds,
            },
            # "all_time_top_artists": all_time_top_artists,
            # "all_time_top_tracks": all_time_top_tracks
        }

    except Exception as e:
        current_app.logger.error("Error while generating analysis: " + str(e))
        return {
            "status": "error"
        }, 400
