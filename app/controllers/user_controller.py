from flask import current_app, make_response, request, Blueprint
from marshmallow import ValidationError
from exceptions.custom_exceptions import SessionExpired, SessionIdNone, SessionIdNotFound

from schemas.SaveUserRequestSchema import SaveUserRequestSchema
from services import user_service
from utils.auth_utils import extend_session_expiry, validate_session

user_controller = Blueprint('user_controller', __name__, url_prefix='/api/user')


@user_controller.route('/save', methods=['POST'])
def save_user():
    """
    Save the user attributes (details and settings preferences)
    If user is new, create entry in users collection
    Get user_id from token
    """
    try:
        spotify_auth = validate_session(request.cookies)

        request_data = request.get_json()
        schema = SaveUserRequestSchema()
        request_body = schema.load(request_data)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except ValidationError as e:
        current_app.logger.error("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.save_user(current_app, spotify_auth, request_body["user_attributes"])


@user_controller.route('/', methods=['GET'])
def get_user():
    """
    Get the user attributes (details and settings preferences)
    If user is not found, error
    Get user_id from token
    """
    try:
        spotify_auth = validate_session(request.cookies)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        response = make_response(user_service.get_user(current_app, spotify_auth))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to retrieve user : " + str(e))
        return {"error": "Unable to retrieve user "}, 400


@user_controller.route('/tracker', methods=['GET'])
def get_user_tracker_data():
    """
    Get the user tracker datapoints
    Pass tracker name in url
    Get user_id from token
    """
    try:
        tracker_name = request.args.get("tracker-name")
        if (tracker_name is None):
            raise Exception("Missing tracker-name")
        spotify_auth = validate_session(request.cookies)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        response = make_response(user_service.handle_get_user_tracker_data(
            current_app, spotify_auth, tracker_name))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to retrieve user tracker data: " + str(e))
        return {"error": "Unable to retrieve user tracker data"}, 400


@user_controller.route('/aggregate', methods=['GET'])
def queue_user_aggregated_data():
    """
    Queue aggregate data task
    """
    try:
        spotify_auth = validate_session(request.cookies)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        response = make_response(user_service.queue_get_aggregate_user_data(spotify_auth))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to get user aggregated data state: " + str(e))
        return {"error": "Unable to get user aggregated data state"}, 400
    
    
@user_controller.route('/aggregate/state/<id>', methods=['GET'])
def get_user_aggregated_data_state(id):
    """
    Get state of aggregate data task
    """
    try:
        spotify_auth = validate_session(request.cookies)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        response = make_response(user_service.get_aggregate_user_data_state(id))
        extend_session_expiry(response, request.cookies)
        return response
    except Exception as e:
        current_app.logger.error(
            "Unable to retrieve user aggregated data: " + str(e))
        return {"error": "Unable to retrieve user aggregated data"}, 400
    