from flask import current_app, request, Blueprint

from services import spotify_auth_service

spotify_auth_controller = Blueprint(
    'spotify_auth_controller', __name__, url_prefix='/api/spotify/auth')


@spotify_auth_controller.route('/login', methods=['GET'])
def get_spotify_uri():
    auth_uri = spotify_auth_service.generate_spotify_auth_uri(current_app)
    return {"loginUri": auth_uri}


@spotify_auth_controller.route('/code', methods=['POST'])
def handle_auth_code():
    try:
        data = request.get_json()
        code = str(data["code"])
        return spotify_auth_service.get_spotify_tokens(current_app, code)
    except Exception as e:
        return {"error": "Unable to authenticate with Spotify"}, 400
