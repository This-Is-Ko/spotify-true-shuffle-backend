import spotipy

from services.spotify_client import *

from schemas.Playlist import Playlist

SHUFFLED_PLAYLIST_PREFIX = "[Shuffled] "
LIKED_TRACKS_PLAYLIST_ID = "likedTracks"


def get_user_playlists(current_app, spotify_access_info):
    auth_manager = create_auth_manager_with_token(
        current_app, spotify_access_info)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if not auth_manager.validate_token(spotify_access_info):
        return {"error": "Invalid token"}, 400
    user = spotify.current_user()

    playlists = spotify.current_user_playlists()
    if not "items" in playlists:
        return {"error": "Unable to retrieve playlists"}, 400

    all_playlists = []
    # Add liked tracks as playlist option
    all_playlists.append(Playlist("Liked Tracks", user, LIKED_TRACKS_PLAYLIST_ID, {
                         "url": "https://misc.scdn.co/liked-songs/liked-songs-300.png"}))
    for playlist_entry in playlists["items"]:
        # Don't select playlists already shuffled
        if playlist_entry["name"].startswith(SHUFFLED_PLAYLIST_PREFIX):
            continue
        all_playlists.append(Playlist(
            playlist_entry["name"], playlist_entry["owner"], playlist_entry["id"], playlist_entry["images"][0]))

    return {"allPlaylists": all_playlists}
