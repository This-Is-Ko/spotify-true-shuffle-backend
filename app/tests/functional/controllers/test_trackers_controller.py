from tests import client, env_patch
import jwt
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

from tests.functional.helpers.mock_requests import *
from tests.functional.helpers.mock_responses import *

# def test_update_trackers_success(mocker, client, env_patch):
#     """
#     Successful GET Update trackers
#     """
#     mocker.patch.object(jwt, "decode",
#                         return_value={
#                                       "sub": "cron",
#                                       "iss": "localhost"
#                                       }
#                         )
#     mocker.patch.object(SpotifyOAuth, "validate_token",
#                         return_value={
#                             "access_token": "access token from spotify",
#                             "refresh_token": "access token from spotify"
#                         }
#                         )
#     mocker.patch.object(Spotify, "current_user",
#                         return_value=mock_user_response)
#     mocker.patch.object(
#         Spotify, "current_user_saved_tracks", return_value=mock_tracks_response)

#     response = client.get('/api/trackers/update',
#                           headers={'Authorization ': 'Bearer eyabc.abc.abc'})
#     response_json = response.get_json()
#     print(response_json)
#     assert response.status_code == 200
