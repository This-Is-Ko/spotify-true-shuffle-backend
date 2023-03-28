from flask import current_app, request, Blueprint

auth_controller = Blueprint(
    'auth_controller', __name__, url_prefix='/api/auth')

# Disabled endpoint


# @auth_controller.route('/access-token', methods=['GET'])
# def get_cron_access_token():
#     """
#     Generate access token for cron job
#     """
#     payload = {
#         "sub": "cron",
#         "iss": current_app.config["JWT_ISSUER"],
#         "admin": True
#     }

#     token = jwt.encode(
#         payload, current_app.config["JWT_SECRET"], algorithm="HS256")
#     return {
#         "x-access-token": token
#     }
