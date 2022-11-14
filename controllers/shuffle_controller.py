from main import app
from flask import request

from services import shuffle

@app.route('/api/shuffle', methods=['POST'])
def shuffle_playlist():
    data = request.get_json()
    if "spotifyAccessInfo" in data and "playlistId" in data and "playlistName" in data:
        return(shuffle.create_shuffled_playlist(data["spotifyAccessInfo"], data["playlistId"], data["playlistName"]))
    return {"error": "Missing spotify access token or playlistId"}, 400