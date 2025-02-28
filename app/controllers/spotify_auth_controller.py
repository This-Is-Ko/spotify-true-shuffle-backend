from flask_cors import cross_origin  # noqa: F401
from flask import current_app, request, Blueprint

from services import spotify_auth_service
from schemas.AuthCodeRequestSchema import AuthCodeRequestSchema
from decorators.schema_validator import request_schema_validator

spotify_auth_controller = Blueprint('spotify_auth_controller', __name__, url_prefix='/api/spotify/auth')


@spotify_auth_controller.route('/login', methods=['GET'])
def get_spotify_uri():
    auth_uri = spotify_auth_service.generate_spotify_auth_uri()
    return {"loginUri": auth_uri}


@spotify_auth_controller.route('/code', methods=['POST'])
@request_schema_validator(AuthCodeRequestSchema)
def handle_auth_code(request_body):
    try:
        code = str(request_body["code"])
        return spotify_auth_service.get_spotify_tokens(code)
    except Exception as e:
        current_app.logger.error("Unable to authenticate with Spotify: " + str(e))
        return {"error": "Unable to authenticate with Spotify"}, 400


@spotify_auth_controller.route('/logout', methods=['POST'])
def logout_user():
    """
    Update cookies to expired to logout user
    """

    return spotify_auth_service.handle_logout(request.cookies)
