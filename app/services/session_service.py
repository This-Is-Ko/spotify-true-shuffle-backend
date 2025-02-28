from datetime import datetime, timezone
from database import database


def handle_clean_up_expired_sesions(current_app):
    delete_response = database.delete_expired_session(
        datetime.now(timezone.utc))
    current_app.logger.info(
        "Cleanup successfully completed. Deleted expired sessions: " + str(delete_response.deleted_count))
    return {
        "status": "success",
        "deleted_count": str(delete_response.deleted_count)
    }
