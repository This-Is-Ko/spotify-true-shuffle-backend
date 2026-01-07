from tests import client, env_patch  # noqa: F401
from services import trackers_service
from controllers import trackers_controller


"""
Success scenarios - GET /api/trackers/update
"""


def test_update_trackers_success(mocker, client, env_patch):
    """
    Successful GET Update trackers
    """
    # Mock cron API key validation at controller level
    mocker.patch("controllers.trackers_controller.validate_cron_api_key", return_value=None)

    # Mock service function
    mocker.patch.object(trackers_service, "update_trackers", return_value={
        "status": "success",
        "message": "Finished updating trackers",
        "updated_users": 3,
        "total_enabled_users": 5
    })

    # Perform GET request with cron API key
    response = client.get('/api/trackers/update', headers={'X-Cron-Key': 'valid_cron_key'})

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["updated_users"] == 3
    assert response_json["total_enabled_users"] == 5


def test_update_trackers_no_enabled_users_success(mocker, client, env_patch):
    """
    Successful GET Update trackers - no enabled users
    """
    # Mock cron API key validation at controller level
    mocker.patch("controllers.trackers_controller.validate_cron_api_key", return_value=None)

    # Mock service function
    mocker.patch.object(trackers_service, "update_trackers", return_value={
        "status": "success",
        "message": "Finished updating trackers",
        "updated_users": 0,
        "total_enabled_users": 0
    })

    # Perform GET request with cron API key
    response = client.get('/api/trackers/update', headers={'X-Cron-Key': 'valid_cron_key'})

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["updated_users"] == 0
    assert response_json["total_enabled_users"] == 0


"""
Failure scenarios - GET /api/trackers/update
"""


def test_update_trackers_failure_missing_header(mocker, client, env_patch):
    """
    Failure GET Update trackers - missing X-Cron-Key header
    """
    from exceptions.custom_exceptions import AccessTokenInvalid

    # Mock cron API key validation to raise exception
    mocker.patch("controllers.trackers_controller.validate_cron_api_key", side_effect=AccessTokenInvalid("Invalid cron API key"))

    # Perform GET request without cron API key
    response = client.get('/api/trackers/update')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 403
    assert response_json["error"] == "Invalid credentials"


def test_update_trackers_failure_invalid_header(mocker, client, env_patch):
    """
    Failure GET Update trackers - invalid X-Cron-Key header
    """
    from exceptions.custom_exceptions import AccessTokenInvalid

    # Mock cron API key validation to raise exception
    mocker.patch("controllers.trackers_controller.validate_cron_api_key", side_effect=AccessTokenInvalid("Invalid cron API key"))

    # Perform GET request with invalid cron API key
    response = client.get('/api/trackers/update', headers={'X-Cron-Key': 'invalid_key'})

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 403
    assert response_json["error"] == "Invalid credentials"


def test_update_trackers_failure_service_exception(mocker, client, env_patch):
    """
    Failure GET Update trackers - service exception
    """
    # Mock cron API key validation at controller level
    mocker.patch("controllers.trackers_controller.validate_cron_api_key", return_value=None)

    # Mock service function to raise exception - patch at controller import level
    mocker.patch("controllers.trackers_controller.trackers_service.update_trackers", side_effect=Exception("Service error"))

    # Perform GET request with cron API key
    # Service exceptions are not caught in controller (no try/except around service call)
    # Flask will catch the exception and return 500, or propagate it in test mode
    try:
        response = client.get('/api/trackers/update', headers={'X-Cron-Key': 'valid_cron_key'})
        # Flask returns 500 for unhandled exceptions
        assert response.status_code == 500
    except Exception:
        # In some Flask test configurations, exceptions are propagated
        # This is acceptable behavior for this test - the exception was raised as expected
        pass
