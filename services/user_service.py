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


def save_user(current_app, spotify_auth, user_attributes):
    """
    Check if user exists and update
    Otherwise create new user entry
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user_entry = {
        "spotify": {
            "expires_at": spotify_auth["expires_at"],
            "refresh_token": spotify_auth["refresh_token"],
            "scope": spotify_auth["scope"]
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


def get_user(current_app, spotify_auth):
    """
    Check if user exists and update
    Otherwise create new user entry
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth):
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


def aggregate_user_data(current_app, spotify_auth):
    """
    Return user trackers and analysis in one call
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth):
        return {"error": "Invalid token"}, 400
    user_id = spotify.me()["id"]
    user = database.find_user(user_id)
    user_json = json.loads(json_util.dumps(user))

     # Increment counter for analysis count
    try:
        overall_counter = database.find_shuffle_counter(
            "overall_counter")
        if overall_counter == None:
            raise Exception("Couldn't find total shuffle counter")

        overall_counter["analysis_count"] = int(
            overall_counter["analysis_count"]) + 1

        overall_counter_update = database.find_and_update_shuffle_counter(
            "overall_counter",
            overall_counter)
    except Exception as e:
        current_app.logger.error(
            "Error updating overall shuffle count: " + str(e))

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


def handle_get_user_tracker_data(current_app, spotify_auth, tracker_name):
    """
    Check if trackers are enabled for user
    If enabled, retrieve all data points for user
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth):
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


def handle_get_user_analysis(current_app, spotify_auth):
    """
    Get all liked tracks to analyse
    Calcuate most common tracks/artists/genres
    """
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_auth)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth):
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
    longest_track_data = {
        "duration_ms": 0
    }
    shortest_track_data = {
        "duration_ms": 0
    }
    # TODO Find oldest and newest tracks
    # oldest_release_date_track = {}
    # latest_release_date_track = {}
    all_tracks_ids = []

    for track in all_tracks:
        track_data = track["track"]
        all_tracks_ids.append(track_data["id"])
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
        # Longest/shortest tracks
        if longest_track_data["duration_ms"] == 0 or int(track_data["duration_ms"]) > longest_track_data["duration_ms"]:
            longest_track_data = track_data
        if shortest_track_data["duration_ms"] == 0 or int(track_data["duration_ms"]) < shortest_track_data["duration_ms"]:
            shortest_track_data = track_data

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
        "shortest_track": prep_essential_track_data(shortest_track_data),
        "longest_track": prep_essential_track_data(longest_track_data),
        "audio_features": audio_features
        # "all_time_top_artists": all_time_top_artists,
        # "all_time_top_tracks": all_time_top_tracks
    }

class TrackFeatureScoreData:
    def __init__(self, feature_name):
        self.feature_name = feature_name
        self.total_score = 0
        self.highest_feature_score = prep_audio_feature_track("", 0)
        self.lowest_feature_score = prep_audio_feature_track("", 0)

    def update_scores(self, track):
        if self.highest_feature_score["id"] == "" or track[self.feature_name] > self.highest_feature_score["value"]:
            self.highest_feature_score = prep_audio_feature_track(track["id"], track[self.feature_name])
        if self.lowest_feature_score["id"] == "" or track[self.feature_name] < self.lowest_feature_score["value"]:
            self.lowest_feature_score = prep_audio_feature_track(track["id"], track[self.feature_name])


def average_audio_features(current_app, spotify, tracks_ids):
    all_audio_features = get_all_track_audio_features(
        current_app, spotify, tracks_ids)
    acousticness_scores = TrackFeatureScoreData("acousticness")
    danceability_scores = TrackFeatureScoreData("danceability")
    energy_scores = TrackFeatureScoreData("energy")
    instrumentalness_scores = TrackFeatureScoreData("instrumentalness")
    liveness_scores = TrackFeatureScoreData("liveness")
    loudness_scores = TrackFeatureScoreData("loudness")
    speechiness_scores = TrackFeatureScoreData("speechiness")
    tempo_scores = TrackFeatureScoreData("tempo")
    valence_scores = TrackFeatureScoreData("valence")

    for track in all_audio_features:
        if track is not None:
            process_track_feature(track, "acousticness", acousticness_scores)
            process_track_feature(track, "danceability", danceability_scores)
            process_track_feature(track, "energy", energy_scores)
            process_track_feature(track, "instrumentalness", instrumentalness_scores)
            process_track_feature(track, "liveness", liveness_scores)
            process_track_feature(track, "loudness", loudness_scores)
            process_track_feature(track, "speechiness", speechiness_scores)
            process_track_feature(track, "tempo", tempo_scores)
            process_track_feature(track, "valence", valence_scores)

    num_tracks = len(tracks_ids)
    average_acousticness = acousticness_scores.total_score / num_tracks
    average_danceability = danceability_scores.total_score / num_tracks
    average_energy = energy_scores.total_score / num_tracks
    average_instrumentalness = instrumentalness_scores.total_score / num_tracks
    average_liveness = liveness_scores.total_score / num_tracks
    average_loudness = loudness_scores.total_score / num_tracks
    average_speechiness = speechiness_scores.total_score / num_tracks
    average_tempo = tempo_scores.total_score / num_tracks
    average_valence = valence_scores.total_score / num_tracks
    return {
        "average_acousticness": average_acousticness,
        "average_danceability": average_danceability,
        "average_energy": average_energy,
        "average_instrumentalness": average_instrumentalness,
        "average_liveness": average_liveness,
        "average_loudness": average_loudness,
        "average_speechiness": average_speechiness,
        "average_tempo": average_tempo,
        "average_valence": average_valence,
        "acousticness_scores": acousticness_scores,
        "danceability_scores": danceability_scores,
        "energy_scores": energy_scores,
        "instrumentalness_scores": instrumentalness_scores,
        "liveness_scores": liveness_scores,
        "loudness_scores": loudness_scores,
        "speechiness_scores": speechiness_scores,
        "tempo_scores": tempo_scores,
        "valence_scores": valence_scores
    }

def prep_audio_feature_track(id, value):
    return {
        "id": id,
        "value": value
    }

def process_track_feature(track, feature_name, feature_score_data):
    if feature_name in track and track[feature_name] is not None:
        feature_score_data.total_score += track[feature_name]
        feature_score_data.update_scores(track)
        

def prep_essential_track_data(track_data):
    if track_data != None:
        return {
            "title": track_data["name"],
            "external_url": track_data["external_urls"]["spotify"],
            "artists": track_data["artists"],
            "length": track_data["duration_ms"],
        }
    return None