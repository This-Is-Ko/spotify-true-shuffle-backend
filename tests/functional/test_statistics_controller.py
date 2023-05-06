from tests import client, env_patch
from database import database


def test_get_statistics_success(mocker, client, env_patch):
    """
    Successful GET Statistics call
    """
    mocker.patch.object(database, "find_shuffle_counter",
                        return_value={
                            "user_id": "overall_counter",
                            "playlist_count": 99,
                            "track_count": 99,
                            "analysis_count": 99,
                        }
                        )
    response = client.get('/api/statistics/overall')
    response_json = response.get_json()
    print(response_json)
    assert response.status_code == 200
    assert response_json["playlist_counter"] == 99
    assert response_json["track_counter"] == 99
    assert response_json["analysis_counter"] == 99


def test_get_statistics_missing_counter_failure(mocker, client, env_patch):
    """
    Failure GET Statistics call
    """
    mocker.patch.object(database, "find_shuffle_counter",
                        return_value=None
                        )
    response = client.get('/api/statistics/overall')
    response_json = response.get_json()
    print(response_json)
    assert response.status_code == 400
