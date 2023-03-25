from flask import current_app, request, Blueprint
from flask_cors import cross_origin
from marshmallow import ValidationError

from services import spotify_auth_service
from schemas.AuthCodeRequestSchema import AuthCodeRequestSchema

spotify_auth_controller = Blueprint(
    'spotify_auth_controller', __name__, url_prefix='/api/spotify/auth')


@spotify_auth_controller.route('/login', methods=['GET'])
def get_spotify_uri():
    auth_uri = spotify_auth_service.generate_spotify_auth_uri(current_app)
    return {"loginUri": auth_uri}


@spotify_auth_controller.route('/code', methods=['POST'])
def handle_auth_code():
    try:
        request_data = request.get_json()
        schema = AuthCodeRequestSchema()
        request_body = schema.load(request_data)
    except ValidationError as e:
        current_app.logger.info("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.info("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    try:
        code = str(request_body["code"])
        return spotify_auth_service.get_spotify_tokens(current_app, code)
    except Exception as e:
        current_app.logger.info(
            "Unable to authenticate with Spotify: " + str(e))
        return {"error": "Unable to authenticate with Spotify"}, 400


@spotify_auth_controller.route('/logout', methods=['POST'])
def logout_user():
    """
    Update cookies to expired to logout user
    """

    return spotify_auth_service.handle_logout(current_app)
