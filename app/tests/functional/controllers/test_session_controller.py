from tests import client, env_patch  # noqa: F401
from database import database
from controllers import session_controller
from services import session_service


"""
Success scenarios - GET /api/session/cleanup
"""


def test_cleanup_expired_sessions_success(mocker, client, env_patch):
    """
    Successful GET cleanup expired sessions request
    """
    # Mock cron API key validation at controller level
    mocker.patch("controllers.session_controller.validate_cron_api_key", return_value=None)

    # Mock database delete operation
    mock_delete_result = mocker.Mock()
    mock_delete_result.deleted_count = 5
    mocker.patch.object(database, "delete_expired_session", return_value=mock_delete_result)

    # Mock service function
    mocker.patch.object(session_service, "handle_clean_up_expired_sesions", return_value={
        "status": "success",
        "deleted_count": "5"
    })

    # Perform GET request with cron API key
    response = client.get('/api/session/cleanup', headers={'X-Cron-Key': 'valid_cron_key'})

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["deleted_count"] == "5"


def test_cleanup_expired_sessions_no_sessions_success(mocker, client, env_patch):
    """
    Successful GET cleanup expired sessions request - no expired sessions
    """
    # Mock cron API key validation at controller level
    mocker.patch("controllers.session_controller.validate_cron_api_key", return_value=None)

    # Mock database delete operation
    mock_delete_result = mocker.Mock()
    mock_delete_result.deleted_count = 0
    mocker.patch.object(database, "delete_expired_session", return_value=mock_delete_result)

    # Mock service function
    mocker.patch.object(session_service, "handle_clean_up_expired_sesions", return_value={
        "status": "success",
        "deleted_count": "0"
    })

    # Perform GET request with cron API key
    response = client.get('/api/session/cleanup', headers={'X-Cron-Key': 'valid_cron_key'})

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["deleted_count"] == "0"


"""
Failure scenarios - GET /api/session/cleanup
"""


def test_cleanup_expired_sessions_failure_missing_header(mocker, client, env_patch):
    """
    Failure GET cleanup expired sessions request - missing X-Cron-Key header
    """
    from exceptions.custom_exceptions import AccessTokenInvalid

    # Mock cron API key validation to raise exception
    mocker.patch("controllers.session_controller.validate_cron_api_key", side_effect=AccessTokenInvalid("Invalid cron API key"))

    # Perform GET request without cron API key
    response = client.get('/api/session/cleanup')

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 403
    assert response_json["error"] == "Invalid credentials"


def test_cleanup_expired_sessions_failure_invalid_header(mocker, client, env_patch):
    """
    Failure GET cleanup expired sessions request - invalid X-Cron-Key header
    """
    from exceptions.custom_exceptions import AccessTokenInvalid

    # Mock cron API key validation to raise exception
    mocker.patch("controllers.session_controller.validate_cron_api_key", side_effect=AccessTokenInvalid("Invalid cron API key"))

    # Perform GET request with invalid cron API key
    response = client.get('/api/session/cleanup', headers={'X-Cron-Key': 'invalid_key'})

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 403
    assert response_json["error"] == "Invalid credentials"


def test_cleanup_expired_sessions_failure_database_error(mocker, client, env_patch):
    """
    Failure GET cleanup expired sessions request - database error
    """
    # Mock cron API key validation at controller level
    mocker.patch("controllers.session_controller.validate_cron_api_key", return_value=None)

    # Mock service function to raise exception - patch at controller import level
    mocker.patch("controllers.session_controller.handle_clean_up_expired_sesions", side_effect=Exception("Database error"))

    # Perform GET request with cron API key
    response = client.get('/api/session/cleanup', headers={'X-Cron-Key': 'valid_cron_key'})

    # Get response JSON
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json["error"] == "Unable to clear expired sessions"

