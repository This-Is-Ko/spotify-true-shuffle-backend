from celery.result import AsyncResult
from flask import current_app

from classes.spotify_auth import SpotifyAuth


def get_celery_task_state(spotify_auth: SpotifyAuth, id: str, type: str):
    user_id = ""
    if not spotify_auth or not spotify_auth.user_id:
        current_app.logger.error("error=missing_user_id")
        # raise ValueError("Missing user_id in Spotify authentication")
    else:
        user_id = spotify_auth.user_id

    result = AsyncResult(id)
    current_app.logger.info(f"type={type}, user_id={user_id}, task_id={id}, state={result.state}")

    if result.state == "PROGRESS":
        return {
                    "state": result.state,
                    "progress": result.info.get("progress", 0)
                }
    elif result.state == "SUCCESS":
        response = {
                    "state": result.state,
                    "result": result.get()
                }
        result.forget()
        return response
    else:
        return {
            "ready": result.ready(),
            "successful": result.successful(),
            "state": result.state
        }
