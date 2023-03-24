from flask import current_app, request, Blueprint
from marshmallow import ValidationError

from schemas.SaveUserRequestSchema import SaveUserRequestSchema
from services import user_service
from utils.utils import create_spotify_auth_object

user_controller = Blueprint(
    'user_controller', __name__, url_prefix='/api/user')


@user_controller.route('/save', methods=['POST'])
def save_user():
    """
    Save the user attributes (details and settings preferences)
    If user is new, create entry in users collection
    Get user_id from token
    """
    try:
        spotify_auth = create_spotify_auth_object(request.cookies)

        request_data = request.get_json()
        schema = SaveUserRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
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
        spotify_auth = create_spotify_auth_object(request.cookies)
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.get_user(current_app, spotify_auth)


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
        spotify_auth = create_spotify_auth_object(request.cookies)
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.handle_get_user_tracker_data(current_app, spotify_auth, tracker_name)


@user_controller.route('/analysis', methods=['GET'])
def get_user_analysis():
    """
    Get user analysis including Liked Tracks data
    Get user_id from token
    """
    try:
        spotify_auth = create_spotify_auth_object(request.cookies)
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.handle_get_user_analysis(current_app, spotify_auth)


@user_controller.route('/aggregate', methods=['GET'])
def get_user_aggregated_data():
    """
    Get user trackers and analysis
    """
    try:
        spotify_auth = create_spotify_auth_object(request.cookies)
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.aggregate_user_data(current_app, spotify_auth)
