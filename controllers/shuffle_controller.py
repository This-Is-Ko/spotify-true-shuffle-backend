from flask import request, Blueprint

from services import shuffle

shuffle_controller = Blueprint(
    'shuffle_controller', __name__, url_prefix='/api/playist')


@shuffle_controller.route('/shuffle', methods=['POST'])
def shuffle_playlist():
    data = request.get_json()
    if "spotifyAccessInfo" in data and "playlistId" in data and "playlistName" in data:
        data["spotifyAccessInfo"]["expires_at"] = int(
            data["spotifyAccessInfo"]["expires_at"])
        return (shuffle.create_shuffled_playlist(data["spotifyAccessInfo"], data["playlistId"], data["playlistName"]))
    return {"error": "Missing spotify access token, playlistId or playlistName"}, 400


@shuffle_controller.route('/delete', methods=['POST'])
def delete_shuffled_playlists():
    data = request.get_json()
    if "spotifyAccessInfo" in data:
        data["spotifyAccessInfo"]["expires_at"] = int(
            data["spotifyAccessInfo"]["expires_at"])
        return (shuffle.delete_all_shuffled_playlists(data["spotifyAccessInfo"]))
    return {"error": "Missing spotify access token"}, 400
