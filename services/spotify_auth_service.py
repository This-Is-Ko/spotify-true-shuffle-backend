from services.spotify_client import *
from services.user_service import save_user


def generate_spotify_auth_uri(current_app):
    auth_manager = create_auth_manager(current_app)
    return auth_manager.get_authorize_url()


def get_spotify_tokens(current_app, code):
    auth_manager = create_auth_manager(current_app)
    auth_response = auth_manager.get_access_token(code=code, check_cache=False)
    if ("access_token") in auth_response:
        # Save user
        save_user_result = save_user(current_app, auth_response, {
                                     "trackers_enabled": True})
        if ("status" in save_user_result and save_user_result["status"] != "success"):
            return {
                "status": "error",
                "error": "Unable to save"
            }
        return auth_response
    else:
        return {"status": "error",
                "error": "Unable to obtain access token"}, 400
