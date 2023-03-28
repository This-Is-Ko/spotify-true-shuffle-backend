
from flask import current_app, request, Blueprint
from exceptions.custom_exceptions import AccessTokenInvalid
from services.session_service import handle_clean_up_expired_sesions

from utils.jwt_auth_utils import validate_auth_header_jwt

session_controller = Blueprint(
    'session_controller', __name__, url_prefix='/api/session')


@session_controller.route('/cleanup', methods=['GET'])
def clean_up_expired_sessions():
    """
    Remove expired sessions from database
    """
    # Verify jwt
    try:
        auth_header = request.headers.get('Authorization')
        validate_auth_header_jwt(auth_header)
    except AccessTokenInvalid as e:
        current_app.logger.error("Error decoding token: " + str(e))
        return {"error": "Invalid credentials"}, 403
    except Exception as e:
        current_app.logger.error("Error decoding token: " + str(e))
        return {"error": "Invalid credentials"}, 403

    try:
        return handle_clean_up_expired_sesions(current_app)
    except Exception as e:
        current_app.logger.error("Unable to clear expired sessions: " + str(e))
        return {"error": "Unable to clear expired sessions"}, 400
