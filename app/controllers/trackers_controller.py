from flask import Blueprint, current_app, request

from exceptions.custom_exceptions import AccessTokenInvalid
from services import trackers_service
from utils.cron_auth_utils import validate_cron_api_key

trackers_controller = Blueprint('trackers_controller', __name__, url_prefix='/api/trackers')


@trackers_controller.route('/update', methods=['GET'])
def update_trackers():
    # Verify cron API key
    try:
        validate_cron_api_key(request)
    except AccessTokenInvalid as e:
        current_app.logger.error("Invalid cron API key: " + str(e))
        return {"error": "Invalid credentials"}, 403
    except Exception as e:
        current_app.logger.error("Error validating cron API key: " + str(e))
        return {"error": "Invalid credentials"}, 403

    current_app.logger.debug("Valid credentials")
    return (trackers_service.update_trackers(current_app))
