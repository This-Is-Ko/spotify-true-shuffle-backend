from flask import current_app, request, Blueprint
from marshmallow import ValidationError

from schemas.SaveUserRequestSchema import SaveUserRequestSchema
from schemas.GetUserRequestSchema import GetUserRequestSchema
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
        schema = SaveUserRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    return user_service.get_user(current_app, request_body["spotify_access_info"])
