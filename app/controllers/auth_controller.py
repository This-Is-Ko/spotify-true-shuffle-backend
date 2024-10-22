from flask import current_app, request, Blueprint
import jwt

from marshmallow import ValidationError
from exceptions.custom_exceptions import SessionExpired, SessionIdNone, SessionIdNotFound
from schemas.ServiceAuthRequestSchema import ServiceAuthRequestSchema

from dotenv import load_dotenv

load_dotenv()

auth_controller = Blueprint('auth_controller', __name__, url_prefix='/api/auth')

@auth_controller.route('/access-token', methods=['POST'])
def get_cron_access_token():
    """
    Generate access token for cron job
    """

    # Validate client id and secret
    try:
        request_data = request.get_json()
        schema = ServiceAuthRequestSchema()
        request_body = schema.load(request_data)
    except (SessionIdNone, SessionIdNotFound, SessionExpired) as e:
        current_app.logger.error("Invalid credentials: " + str(e))
        return {"error": "Invalid credentials"}, 401
    except ValidationError as e:
        current_app.logger.error("Invalid request: " + str(e.messages))
        return {"error": "Invalid request"}, 400
    except Exception as e:
        current_app.logger.error("Invalid request: " + str(e))
        return {"error": "Invalid request"}, 400

    client_id = current_app.config["SERVICE_CLIENT_ID"]
    if client_id is None or client_id != request_body["client_id"]:
        return {"error": "Invalid credentials"}, 401
    
    client_secret = current_app.config["SERVICE_CLIENT_SECRET"]
    if client_secret is None or client_secret != request_body["client_secret"]:
        return {"error": "Invalid credentials"}, 401
        
    payload = {
        "sub": client_id,
        "iss": current_app.config["JWT_ISSUER"],
        "admin": True
    }
    token = jwt.encode(
        payload, current_app.config["JWT_SECRET"], algorithm="HS256")
    return {
        "x-access-token": token
    }
