from flask import current_app, Blueprint
import jwt

from schemas.ServiceAuthRequestSchema import ServiceAuthRequestSchema
from decorators.schema_validator import request_schema_validator

from dotenv import load_dotenv

load_dotenv()

auth_controller = Blueprint('auth_controller', __name__, url_prefix='/api/auth')


@auth_controller.route('/access-token', methods=['POST'])
@request_schema_validator(ServiceAuthRequestSchema)
def get_cron_access_token(request_body):
    """
    Generate access token for cron job
    """

    # Validate client id and secret
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
    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")
    return {
        "x-access-token": token
    }
