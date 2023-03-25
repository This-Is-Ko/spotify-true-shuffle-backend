from flask import Blueprint, current_app, request
import jwt
from services import trackers_service

trackers_controller = Blueprint(
    'trackers_controller', __name__, url_prefix='/api/trackers')


@trackers_controller.route('/update', methods=['GET'])
def update_trackers():
    # Verify jwt
    auth_header = request.headers.get('Authorization')
    auth_token = ""
    if auth_header == None:
        return {"error": "Invalid credentials"}, 401

    try:
        auth_token = auth_header.split(" ")[1]
    except IndexError as e:
        current_app.logger.info("Invalid credentials: " + str(e.messages))
        return {"error": "Invalid credentials"}, 401

    try:
        decoded_token = jwt.decode(
            auth_token,
            current_app.config["JWT_SECRET"],
            verify=True,
            algorithms=["HS256"],
            issuer=current_app.config["JWT_ISSUER"])

        # Check sub
        if "sub" not in decoded_token or decoded_token["sub"] != "cron":
            current_app.logger.info(
                "Error decoding token: " + "sub claim missing or invalid in token")
            return {"error": "Invalid credentials"}, 403
        # Check admin
        if "admin" not in decoded_token or decoded_token["admin"] != True:
            current_app.logger.info(
                "Error decoding token: " + "admin claim missing or invalid in token")
            return {"error": "Invalid credentials"}, 403

    except jwt.InvalidIssuerError as e:
        current_app.logger.info("Error decoding token: " + str(e))
        return {"error": "Invalid credentials"}, 403
    except jwt.DecodeError as e:
        current_app.logger.info(
            "Error decoding token: " + str(e))
        return {"error": "Invalid credentials"}, 403

    current_app.logger.debug("Valid credentials")
    return (trackers_service.update_trackers(current_app))
