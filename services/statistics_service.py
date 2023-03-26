from database import database

PLAYLIST_COUNTER_FILE = "/playlist_counter.txt"
TRACK_COUNTER_FILE = "/track_counter.txt"


def get_overall_statistics(current_app):
    try:
        # Retrieve counters for playlists and tracks
        total_shuffle_counter = database.find_shuffle_counter(
            "overall_counter")
        if total_shuffle_counter == None:
            current_app.logger.error(
                "Error finding overall shuffle count")
            raise Exception("Couldn't find overall shuffle counter")
        return {
            "status": "success",
            "playlist_counter": total_shuffle_counter["playlist_count"],
            "track_counter": total_shuffle_counter["track_count"]
        }
    except Exception as e:
        current_app.logger.error("Unable to retrieve statistics: " + str(e))
        return {"error": "Unable to retrieve statistics"}, 400
