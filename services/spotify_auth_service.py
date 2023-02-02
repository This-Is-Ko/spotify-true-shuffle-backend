from services.spotify_client import *


def generate_spotify_auth_uri(current_app):
    auth_manager = create_auth_manager(current_app)
    return auth_manager.get_authorize_url()


def get_spotify_tokens(current_app, code):
    auth_manager = create_auth_manager(current_app)
    auth_response = auth_manager.get_access_token(code=code, check_cache=False)
    if ("access_token") in auth_response:
        return auth_response
    else:
        return {"error": "Unable to obtain access token"}, 400
