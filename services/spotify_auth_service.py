from flask import make_response
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
        response = make_response()
        response.set_cookie(key="trueshuffle-spotifyAccessToken",
                            value=auth_response["access_token"],
                            # domain="127.0.0.1"
                            )
        response.set_cookie(key="trueshuffle-spotifyRefreshToken",
                            value=auth_response["refresh_token"],
                            # domain="127.0.0.1"
                            )
        response.set_cookie(key="trueshuffle-spotifyExpiresAt",
                            value=str(auth_response["expires_at"]),
                            # domain="127.0.0.1"
                            )
        response.set_cookie(key="trueshuffle-spotifyScope",
                            value=auth_response["scope"],
                            # domain="127.0.0.1"
                            )
        return response
    else:
        return {"status": "error",
                "error": "Unable to obtain access token"}, 400


def handle_logout(current_app):
    response = make_response()
    response.set_cookie(key="trueshuffle-spotifyAccessToken",
                            value="",
                            expires=0
                        )
    response.set_cookie(key="trueshuffle-spotifyRefreshToken",
                            value="",
                            expires=0
                        )
    response.set_cookie(key="trueshuffle-spotifyExpiresAt",
                            value="",
                            expires=0
                        )
    response.set_cookie(key="trueshuffle-spotifyScope",
                            value="",
                            expires=0
                        )
    current_app.logger.debug("Logging out user")
    return response
