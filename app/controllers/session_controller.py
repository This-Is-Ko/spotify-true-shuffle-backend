from flask import current_app, request, Blueprint

from exceptions.custom_exceptions import AccessTokenInvalid
from services.session_service import handle_clean_up_expired_sesions
from utils.cron_auth_utils import validate_cron_api_key

session_controller = Blueprint('session_controller', __name__, url_prefix='/api/session')


@session_controller.route('/cleanup', methods=['GET'])
def clean_up_expired_sessions():
    """
    Removes expired sessions from database
    """
    # Verify cron API key
    try:
        validate_cron_api_key(request)
    except AccessTokenInvalid as e:
        current_app.logger.error("Invalid cron API key: " + str(e))
        return {"error": "Invalid credentials"}, 403
    except Exception as e:
        current_app.logger.error("Error validating cron API key: " + str(e))
        return {"error": "Invalid credentials"}, 403

    try:
        return handle_clean_up_expired_sesions(current_app)
    except Exception as e:
        current_app.logger.error("Unable to clear expired sessions: " + str(e))
        return {"error": "Unable to clear expired sessions"}, 400
