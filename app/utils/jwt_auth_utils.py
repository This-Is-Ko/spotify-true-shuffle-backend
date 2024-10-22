from flask import current_app, request
import jwt

from exceptions.custom_exceptions import AccessTokenInvalid


def validate_auth_header_jwt(auth_header):
    auth_token = ""
    if auth_header == None:
        raise AccessTokenInvalid("Access token missing")

    auth_token = auth_header.split(" ")[1]

    try:
        decoded_token = jwt.decode(
            auth_token,
            current_app.config["JWT_SECRET"],
            verify=True,
            algorithms=["HS256"],
            issuer=current_app.config["JWT_ISSUER"])
    except jwt.InvalidIssuerError as e:
        raise AccessTokenInvalid(
            "iss claim missing or invalid in token")
    except jwt.DecodeError as e:
        raise AccessTokenInvalid(str(e))
    # Check sub
    
    client_id = current_app.config["SERVICE_CLIENT_ID"]
    if client_id is None:
        AccessTokenInvalid("sub invalid in token")
    
    if "sub" not in decoded_token or decoded_token["sub"] != client_id:
        raise AccessTokenInvalid(
            "sub claim missing or invalid in token")
    # Check admin
    if "admin" not in decoded_token or decoded_token["admin"] != True:
        raise AccessTokenInvalid(
            "admin claim missing or invalid in token")
