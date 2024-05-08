from flask import Blueprint, current_app, request
import jwt
from exceptions.custom_exceptions import AccessTokenInvalid
from services import trackers_service
from utils.jwt_auth_utils import validate_auth_header_jwt

trackers_controller = Blueprint('trackers_controller', __name__, url_prefix='/api/trackers')


@trackers_controller.route('/update', methods=['GET'])
def update_trackers():
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

    current_app.logger.debug("Valid credentials")
    return (trackers_service.update_trackers(current_app))
