from flask import current_app, request, Blueprint
from marshmallow import ValidationError

from schemas.SaveUserRequestSchema import SaveUserRequestSchema
from schemas.GetUserRequestSchema import GetUserRequestSchema
from schemas.GetUserAnalysisRequestSchema import GetUserAnalysisRequestSchema
from schemas.GetUserTrackerDataRequestSchema import GetUserTrackerDataRequestSchema
from services import user_service

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
        request_data = request.get_json()
        schema = SaveUserRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.save_user(current_app, request_body["spotify_access_info"], request_body["user_attributes"])


@user_controller.route('/', methods=['POST'])
def get_user():
    """
    Get the user attributes (details and settings preferences)
    If user is not found, error
    Get user_id from token
    """
    try:
        request_data = request.get_json()
        schema = GetUserRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.get_user(current_app, request_body["spotify_access_info"])


@user_controller.route('/tracker', methods=['POST'])
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
        request_data = request.get_json()
        schema = GetUserTrackerDataRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.handle_get_user_tracker_data(current_app, request_body["spotify_access_info"], tracker_name)


@user_controller.route('/analysis', methods=['POST'])
def get_user_analysis():
    """
    Get user analysis including Liked Tracks data
    Get user_id from token
    """
    try:
        request_data = request.get_json()
        schema = GetUserAnalysisRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.handle_get_user_analysis(current_app, request_body["spotify_access_info"])


@user_controller.route('/aggregate', methods=['POST'])
def get_user_aggregated_data():
    """
    Get user trackers and analysis
    """
    try:
        request_data = request.get_json()
        schema = GetUserAnalysisRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.aggregate_user_data(current_app, request_body["spotify_access_info"])
