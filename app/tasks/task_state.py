from celery.result import AsyncResult
from flask import current_app

from classes.spotify_auth import SpotifyAuth
from utils.logger_utils import logError, logInfo


def get_celery_task_state(spotify_auth: SpotifyAuth, id: str, type: str):
    user_id = ""
    if not spotify_auth or not spotify_auth.user_id:
        logError("Missing user_id")
        raise ValueError("Missing user_id in Spotify authentication")
    else:
        user_id = spotify_auth.user_id

    result = AsyncResult(id)
    
    # Extract correlation_id from task metadata
    correlation_id = None
    try:
        if result.info and isinstance(result.info, dict):
            correlation_id = result.info.get("correlation_id")
    except Exception:
        pass
    
    logInfo(f"user_id={user_id} - type={type} - task_id={id} - state={result.state}")

    if result.state == "PROGRESS":
        response = {
                    "state": result.state,
                    "progress": result.info.get("progress", 0) if isinstance(result.info, dict) else 0
                }
        if correlation_id:
            response["correlation_id"] = correlation_id
        return response
    elif result.state == "SUCCESS":
        response = {
                    "state": result.state,
                    "result": result.get()
                }
        if correlation_id:
            response["correlation_id"] = correlation_id
        result.forget()
        return response
    else:
        response = {
            "ready": result.ready(),
            "successful": result.successful(),
            "state": result.state
        }
        if correlation_id:
            response["correlation_id"] = correlation_id
        return response
