from database import database

PLAYLIST_COUNTER_FILE = "/playlist_counter.txt"
TRACK_COUNTER_FILE = "/track_counter.txt"


def get_overall_statistics(current_app):
    try:
        # Retrieve counters for playlists and tracks
        overall_counter = database.find_shuffle_counter(
            "overall_counter")
        if overall_counter is None:
            current_app.logger.error("Error finding overall counter")
            raise Exception("Couldn't find overall counter")
        return {
            "status": "success",
            "playlist_counter": overall_counter["playlist_count"],
            "track_counter": overall_counter["track_count"],
            "analysis_counter": overall_counter["analysis_count"]
        }
    except Exception as e:
        current_app.logger.error("Unable to retrieve statistics: " + str(e))
        return {"error": "Unable to retrieve statistics"}, 400
