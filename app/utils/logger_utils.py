from flask import current_app

def logErrorWithUser(message: str, spotify_auth=None):
    # Log message with user_id if available
    if spotify_auth and spotify_auth.user_id:
        message = f"User ID: {spotify_auth.user_id} - " + message
    
    current_app.logger.error(message)

def logInfoWithUser(message: str, spotify_auth=None):
    # Log message with user_id if available
    if spotify_auth and spotify_auth.user_id:
        message = f"User ID: {spotify_auth.user_id} - " + message
    
    current_app.logger.info(message)
