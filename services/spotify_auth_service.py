from flask import make_response
import jwt

from services.spotify_client import *
from services.user_service import save_user
from database import database
from utils.auth_utils import generate_hashed_session_id, generate_session_id


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

        # Prepare session entry
        # Schema:
        #    user_id
        #    session_id
        #    access_token
        #    refresh_token
        #    expires_at
        #    scope
        try:
            user_id = save_user_result["user"]["user_id"]
            spotify_auth = dict()
            session_id = generate_session_id()
            spotify_auth["session_id"] = generate_hashed_session_id(session_id)
            spotify_auth["access_token"] = auth_response["access_token"]
            spotify_auth["refresh_token"] = auth_response["refresh_token"]
            spotify_auth["expires_at"] = auth_response["expires_at"]
            spotify_auth["scope"] = auth_response["scope"]
            session = database.find_and_update_session(
                user_id, spotify_auth)
            if session is None:
                raise Exception("Unable to save session in database")
        except Exception as e:
            current_app.logger.error(
                "Failed to create session: " + str(e))
            return {"status": "error",
                    "error": "Unable to create session"}, 400

        response.set_cookie(key="trueshuffle-sessionId",
                            value=session_id,
                            httponly=True,
                            domain=current_app.config["COOKIE_DOMAIN"],
                            samesite='None',
                            secure=True
                            )
        response.set_cookie(key="trueshuffle-auth",
                            value="true",
                            domain=current_app.config["COOKIE_DOMAIN_AUTH_STATUS"],
                            samesite='None',
                            secure=True
                            )

        return response
    else:
        return {"status": "error",
                "error": "Unable to create session"}, 400


def handle_logout(current_app, cookies):
    response = make_response()
    current_app.logger.debug("Logging out user")

    # Set cookies to expired
    response.set_cookie(key="trueshuffle-sessionId",
                            value="",
                            expires=0
                        )
    response.set_cookie(key="trueshuffle-auth",
                            value="",
                            expires=0
                        )

    try:
        session_id = cookies.get("trueshuffle-sessionId")
        # Remove session from db
        database.delete_session(generate_hashed_session_id(session_id))
    except Exception as e:
        current_app.logger.error(
            "Error decoding access token/deleting session: " + str(e))

    return response
