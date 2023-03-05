from database import database
import spotipy
from bson import json_util
import json

from services.spotify_client import *
from utils.utils import *

LIKED_TRACKS_PLAYLIST_ID = "likedTracks"

TRACKERS_ENABLED_ATTRIBUTE_NAME = "trackers_enabled"
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
    }, 400


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


def aggregate_user_data(current_app, spotify_access_info):
    """
    Return user trackers and analysis in one call
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user = database.find_user(user_id)
    user_json = json.loads(json_util.dumps(user))

    try:
        return {
            TRACK_LIKED_TRACKS_ATTRIBUTE_NAME: get_user_tracker_data(user_id, user_json,
                                                                     TRACK_LIKED_TRACKS_ATTRIBUTE_NAME),
            "analysis": get_user_analysis(current_app, spotify)
        }
    except Exception as e:
        current_app.logger.error(
            "Error in aggregate_user_data: " + str(e))
        return {
            "status": "error"
        }, 400


def handle_get_user_tracker_data(current_app, spotify_access_info, tracker_name):
    """
    Check if trackers are enabled for user
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
    try:
        return get_user_tracker_data(user_id, user_json, tracker_name)
    except Exception as e:
        current_app.logger.error(
            "Error in handle_get_user_tracker_data: " + str(e))
        return {
            "status": "error"
        }, 400


def get_user_tracker_data(user_id, user_json, tracker_name):
    # Check tracker status
    if (TRACKERS_ENABLED_ATTRIBUTE_NAME not in user_json["user_attributes"] or user_json["user_attributes"][TRACKERS_ENABLED_ATTRIBUTE_NAME] is not True):
        raise Exception("Trackers not enabled")
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


def handle_get_user_analysis(current_app, spotify_access_info):
    """
    Get all liked tracks to analyse
    Calcuate most common tracks/artists/genres
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    try:
        return get_user_analysis(current_app, spotify)
    except Exception as e:
        current_app.logger.error(
            "Error in handle_get_user_analysis: " + str(e))
        return {
            "status": "error"
        }, 400


def get_user_analysis(current_app, spotify):
    # Get all tracks from library
    all_tracks = get_all_tracks_with_data_from_playlist(
        spotify, LIKED_TRACKS_PLAYLIST_ID)
    num_tracks = len(all_tracks)

    if num_tracks == 0:
        return {
            "num_tracks": num_tracks,
            "num_artists": 0,
            "num_albums": 0,
            "most_common_artists": [],
            "most_common_albums": [],
            "most_common_genre": [],
            "total_length": {
                "days": 0,
                "hours": 0,
                "minutes": 0,
                "seconds": 0,
            },
            "average_track_length": {
                "days": 0,
                "hours": 0,
                "minutes": 0,
                "seconds": 0,
            },
            "audio_features": {}
            # "all_time_top_artists": [],
            # "all_time_top_tracks": []
        }

    most_common_artists = {}
    most_common_albums = {}
    most_common_genre = {}
    total_length = 0
    average_track_length = 0
    # TODO Find oldest and newest tracks
    # oldest_release_date_track = {}
    # latest_release_date_track = {}
    all_tracks_ids = []

    for track in all_tracks:
        track_data = track["track"]
        all_tracks_ids.append(track_data["id"])
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
            album_artist = ""
            if "artists" in artist:
                album_artist = album["artists"][0]["name"]
            most_common_albums[album["name"]] = {
                "id": album["id"],
                "name": album["name"],
                "artist": album_artist,
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

    average_track_length = total_length / num_tracks
    average_track_length_seconds, average_track_length_minutes, average_track_length_hours, average_track_length_days = calcFromMillis(
        average_track_length)
    total_length_seconds, total_length_minutes, total_length_hours, total_length_days = calcFromMillis(
        total_length)

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

    try:
        audio_features = average_audio_features(
            current_app, spotify, all_tracks_ids)
    except Exception as e:
        current_app.logger.error(
            "Failed while retrieving/calculating audio features: " + str(e))
        raise Exception(
            "Failed while retrieving/calculating audio features: " + str(e))

    return {
        "num_tracks": num_tracks,
        "num_artists": len(most_common_artists_array),
        "num_albums": len(most_common_albums_array),
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
        "audio_features": audio_features
        # "all_time_top_artists": all_time_top_artists,
        # "all_time_top_tracks": all_time_top_tracks
    }


def average_audio_features(current_app, spotify, tracks_ids):
    all_audio_features = get_all_track_audio_features(
        current_app, spotify, tracks_ids)
    acousticness = 0
    danceability = 0
    energy = 0
    instrumentalness = 0
    liveness = 0
    loudness = 0
    speechiness = 0
    tempo = 0
    for track in all_audio_features:
        if track is not None:
            if "acousticness" in track and track["acousticness"] is not None:
                acousticness += track["acousticness"]
            if "danceability" in track and track["danceability"] is not None:
                danceability += track["danceability"]
            if "energy" in track and track["energy"] is not None:
                energy += track["energy"]
            if "instrumentalness" in track and track["instrumentalness"] is not None:
                instrumentalness += track["instrumentalness"]
            if "liveness" in track and track["liveness"] is not None:
                liveness += track["liveness"]
            if "loudness" in track and track["loudness"] is not None:
                loudness += track["loudness"]
            if "speechiness" in track and track["speechiness"] is not None:
                speechiness += track["speechiness"]
            if "tempo" in track and track["tempo"] is not None:
                tempo += track["tempo"]
    num_tracks = len(tracks_ids)
    average_acousticness = acousticness / num_tracks
    average_danceability = danceability / num_tracks
    average_energy = energy / num_tracks
    average_instrumentalness = instrumentalness / num_tracks
    average_liveness = liveness / num_tracks
    average_loudness = loudness / num_tracks
    average_speechiness = speechiness / num_tracks
    average_tempo = tempo / num_tracks
    return {
        "average_acousticness": average_acousticness,
        "average_danceability": average_danceability,
        "average_energy": average_energy,
        "average_instrumentalness": average_instrumentalness,
        "average_liveness": average_liveness,
        "average_loudness": average_loudness,
        "average_speechiness": average_speechiness,
        "average_tempo": average_tempo
    }
