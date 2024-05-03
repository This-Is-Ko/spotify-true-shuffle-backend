from celery import shared_task
from flask import current_app
import spotipy
from bson import json_util
import json

from database import database
from services.spotify_client import create_auth_manager_with_token_dict
from utils.util import *

TRACKERS_ENABLED_ATTRIBUTE_NAME = "trackers_enabled"
TRACK_LIKED_TRACKS_ATTRIBUTE_NAME = "track_liked_tracks"
TRACK_SHUFFLES_ATTRIBUTE_NAME = "track_shuffles"
ANALYSE_LIBRARY_ATTRIBUTE_NAME = "analyse_library"

@shared_task(bind=True, ignore_result=False)
def aggregate_user_data(self, spotify_auth_dict: dict):
    """
    Return user trackers and analysis in one call
    """
    auth_manager = create_auth_manager_with_token_dict(
        current_app, spotify_auth_dict)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_auth_dict):
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
            "status": "success",
            TRACK_LIKED_TRACKS_ATTRIBUTE_NAME: get_user_tracker_data(self, user_id, user_json,
                                                                     TRACK_LIKED_TRACKS_ATTRIBUTE_NAME),
            "analysis": get_user_analysis(self, current_app, spotify)
        }
    except Exception as e:
        current_app.logger.error(
            "Error in aggregate_user_data: " + str(e))
        return {
            "status": "error"
        }, 400


def get_user_tracker_data(task, user_id, user_json, tracker_name):
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
    task.update_state(state='PROGRESS', meta={'progress': {'state': "Getting history tracker data"}})
    return {
        "status": "success",
        "data": data
    }


def get_user_analysis(task, current_app, spotify: spotipy.Spotify):
    # Get all tracks from library
    all_tracks = get_all_tracks_with_data_from_playlist(task, 
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
    sorted_tracks = sorted(all_tracks, key=lambda track: int(track["track"]["duration_ms"]), reverse=True)
    top_10_longest_tracks = sorted_tracks[:10]
    top_10_shortest_tracks = sorted(sorted_tracks[len(sorted_tracks)-10:], key=lambda track: int(track["track"]["duration_ms"]))
    release_year_counts = {}

    # TODO Find oldest and newest tracks
    # oldest_release_date_track = {}
    # latest_release_date_track = {}
    all_tracks_ids = []

    counter = 1

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
        # Release date
        release_date = album["release_date"]

        try:
            release_date_object = datetime.strptime(release_date, '%Y-%m-%d').date()
            if release_date_object.year in release_year_counts:
                release_year_counts[release_date_object.year] += 1
            else:
                release_year_counts[release_date_object.year] = 1
        except Exception as e:
            try:
                release_date_object = datetime.strptime(release_date, '%Y').date()
                if release_date_object.year in release_year_counts:
                    release_year_counts[release_date_object.year] += 1
                else:
                    release_year_counts[release_date_object.year] = 1
            except Exception as e:
                release_date_object = datetime.strptime(release_date, '%Y-%m').date()
                if release_date_object.year in release_year_counts:
                    release_year_counts[release_date_object.year] += 1
                else:
                    release_year_counts[release_date_object.year] = 1
        task.update_state(state='PROGRESS', meta={'progress': {'state': "Analysed " + str(counter) + " tracks so far..."}})
        counter = counter + 1
    
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
        audio_features = average_audio_features(task, spotify, all_tracks_ids)
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
        "longest_tracks": process_multiple_tracks(top_10_longest_tracks),
        "shortest_tracks": process_multiple_tracks(top_10_shortest_tracks),
        "release_year_counts": release_year_counts,
        "audio_features": audio_features
        # "all_time_top_artists": all_time_top_artists,
        # "all_time_top_tracks": all_time_top_tracks
    }

class TrackFeatureScoreData:
    def __init__(self, feature_name, feature_description):
        self.feature_name = feature_name
        self.feature_description = feature_description
        self.total_score = 0
        self.average_score = 0
        self.highest_feature_score = prep_audio_feature_track("", 0)
        self.lowest_feature_score = prep_audio_feature_track("", 0)

    def update_scores(self, track):
        if self.highest_feature_score["id"] == "" or track[self.feature_name] > self.highest_feature_score["value"]:
            self.highest_feature_score = prep_audio_feature_track(track["id"], track[self.feature_name])
        if self.lowest_feature_score["id"] == "" or track[self.feature_name] < self.lowest_feature_score["value"]:
            self.lowest_feature_score = prep_audio_feature_track(track["id"], track[self.feature_name])

    def to_dict(self):
        return {
            'feature_name': self.feature_name,
            'feature_description': self.feature_description,
            'total_score': self.total_score,
            'average_score': self.average_score,
            'highest_feature_score': self.highest_feature_score,
            'lowest_feature_score': self.lowest_feature_score
        }

def average_audio_features(task, spotify: spotipy.Spotify, tracks_ids):
    all_audio_features = get_all_track_audio_features(task, spotify, tracks_ids)
    acousticness_scores = TrackFeatureScoreData("acousticness", """A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.""")
    danceability_scores = TrackFeatureScoreData("danceability", """Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.""")
    energy_scores = TrackFeatureScoreData("energy", """Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy.""")
    instrumentalness_scores = TrackFeatureScoreData("instrumentalness", """Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.""")
    liveness_scores = TrackFeatureScoreData("liveness", """Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.""")
    loudness_scores = TrackFeatureScoreData("loudness", """The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 db.""")
    speechiness_scores = TrackFeatureScoreData("speechiness", """Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.""")
    tempo_scores = TrackFeatureScoreData("tempo", """The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.""")
    valence_scores = TrackFeatureScoreData("valence", """A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).""")

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

    # Update averages
    num_tracks = len(tracks_ids)
    acousticness_scores.average_score = acousticness_scores.total_score / num_tracks
    danceability_scores.average_score = danceability_scores.total_score / num_tracks
    energy_scores.average_score = energy_scores.total_score / num_tracks
    instrumentalness_scores.average_score = instrumentalness_scores.total_score / num_tracks
    liveness_scores.average_score = liveness_scores.total_score / num_tracks
    loudness_scores.average_score = loudness_scores.total_score / num_tracks
    speechiness_scores.average_score = speechiness_scores.total_score / num_tracks
    tempo_scores.average_score = tempo_scores.total_score / num_tracks
    valence_scores.average_score = valence_scores.total_score / num_tracks

    all_features = [
        acousticness_scores.to_dict(),
        danceability_scores.to_dict(),
        energy_scores.to_dict(),
        instrumentalness_scores.to_dict(),
        liveness_scores.to_dict(),
        loudness_scores.to_dict(),
        speechiness_scores.to_dict(),
        tempo_scores.to_dict(),
        valence_scores.to_dict()
    ]

    return all_features

def prep_audio_feature_track(id, value):
    return {
        "id": id,
        "value": value
    }

def process_track_feature(track, feature_name, feature_score_data):
    if feature_name in track and track[feature_name] is not None:
        feature_score_data.total_score += track[feature_name]
        feature_score_data.update_scores(track)
        

def process_multiple_tracks(tracks):
    processed_tracks = []
    for track_data in tracks:
        processed_tracks.append(prep_essential_track_data(track_data["track"]))
    return processed_tracks


def prep_essential_track_data(track_data):
    if track_data != None:
        try:
            track_length_seconds, track_length_minutes, track_length_hours, track_length_days = calcFromMillis(track_data["duration_ms"])
            return {
                "title": track_data["name"],
                "external_url": track_data["external_urls"]["spotify"],
                "artists": track_data["artists"],
                "length": {
                    "days": track_length_days,
                    "hours": track_length_hours,
                    "minutes": track_length_minutes,
                    "seconds": track_length_seconds,
                },
                "preview_url": track_data["preview_url"],
                "album": {
                    "name": track_data["album"]["name"],
                    "image_url": track_data["album"]["images"][1]["url"]
                },
            }
        except Exception as e:
            return None
    return None