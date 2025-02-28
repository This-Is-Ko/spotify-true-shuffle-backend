from database import database

PLAYLIST_COUNTER_FILE = "/playlist_counter.txt"
TRACK_COUNTER_FILE = "/track_counter.txt"


def get_overall_statistics(current_app, is_full_stats: bool):
    try:
        # Retrieve counters for playlists and tracks
        overall_counter = database.find_shuffle_counter(
            "overall_counter")
        if overall_counter is None:
            current_app.logger.error("Error finding overall counter")
            raise Exception("Couldn't find overall counter")

        top_tracks = None
        top_artists = None
        if is_full_stats:
            # Retrieve top 10 tracks by shuffle count
            top_tracks = list(database.get_top_tracks(limit=10))
            # spotify = spotipy.Spotify(auth_manager=auth_manager)
            # spotify.tracks()

            # Retrieve top 10 artists by aggregating shuffle counts from all tracks
            top_artists = list(database.get_top_artists(limit=10))

        return {
            "status": "success",
            "playlist_counter": overall_counter["playlist_count"],
            "track_counter": overall_counter["track_count"],
            "analysis_counter": overall_counter["analysis_count"],
            "top_tracks": top_tracks,
            "top_artists": top_artists
        }
    except Exception as e:
        current_app.logger.error("Unable to retrieve statistics: " + str(e))
        return {"error": "Unable to retrieve statistics"}, 400
