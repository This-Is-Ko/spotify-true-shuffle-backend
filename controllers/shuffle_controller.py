from main import app
from flask import request

from services import shuffle

@app.route('/api/playist/shuffle', methods=['POST'])
def shuffle_playlist():
    data = request.get_json()
    if "spotifyAccessInfo" in data and "playlistId" in data and "playlistName" in data:
        data["spotifyAccessInfo"]["expires_at"] = int(data["spotifyAccessInfo"]["expires_at"])
        return(shuffle.create_shuffled_playlist(data["spotifyAccessInfo"], data["playlistId"], data["playlistName"]))
    return {"error": "Missing spotify access token, playlistId or playlistName"}, 400

@app.route('/api/playist/delete', methods=['POST'])
def delete_shuffled_playlists():
    data = request.get_json()
    if "spotifyAccessInfo" in data:
        data["spotifyAccessInfo"]["expires_at"] = int(data["spotifyAccessInfo"]["expires_at"])
        return(shuffle.delete_all_shuffled_playlists(data["spotifyAccessInfo"]))
    return {"error": "Missing spotify access token"}, 400
