import os

PLAYLIST_COUNTER_FILE = "/playlist_counter.txt"
TRACK_COUNTER_FILE = "/track_counter.txt"

def get_overall_statistics():
    try:
    # Retrieve counters for playlists and tracks
        with open(os.environ.get("COUNTER_DIRECTORY") + PLAYLIST_COUNTER_FILE, 'r') as f:
            playlist_counter=f.read()
        
        with open(os.environ.get("COUNTER_DIRECTORY") + TRACK_COUNTER_FILE, 'r') as f:
            track_counter=f.read()
    
        return {
            "status": "success", 
            "playlist_counter": playlist_counter,
            "track_counter": track_counter
        }
    except Exception as e:
        return {"error": "Unable to retrieve statistics" + e}, 400

