from flask import current_app, g
from celery import current_task

def get_correlation_id():
    """Get correlation ID from Flask g object or Celery task metadata"""
    # Try Flask request context first
    try:
        if hasattr(g, 'correlation_id'):
            return g.correlation_id
    except RuntimeError:
        # Not in Flask request context (e.g., in Celery task)
        pass
    
    # Try Celery task metadata
    try:
        if current_task and hasattr(current_task, 'request') and current_task.request:
            task_meta = current_task.request.get('meta', {})
            if isinstance(task_meta, dict):
                return task_meta.get('correlation_id')
    except Exception:
        pass
    
    return None

def logErrorWithUser(message: str, spotify_auth=None):
    # Get correlation ID
    correlation_id = get_correlation_id()
    
    # Build log message with correlation ID and user_id if available
    log_parts = []
    if correlation_id:
        log_parts.append(f"[Correlation-ID: {correlation_id}]")
    if spotify_auth and spotify_auth.user_id:
        log_parts.append(f"User ID: {spotify_auth.user_id}")
    
    if log_parts:
        message = " - ".join(log_parts) + " - " + message
    
    current_app.logger.error(message)

def logInfoWithUser(message: str, spotify_auth=None):
    # Get correlation ID
    correlation_id = get_correlation_id()
    
    # Build log message with correlation ID and user_id if available
    log_parts = []
    if correlation_id:
        log_parts.append(f"[Correlation-ID: {correlation_id}]")
    if spotify_auth and spotify_auth.user_id:
        log_parts.append(f"User ID: {spotify_auth.user_id}")
    
    if log_parts:
        message = " - ".join(log_parts) + " - " + message
    
    current_app.logger.info(message)


def logError(message: str):
    """Log error message with correlation ID if available"""
    correlation_id = get_correlation_id()
    if correlation_id:
        message = f"[Correlation-ID: {correlation_id}] - " + message
    current_app.logger.error(message)


def logInfo(message: str):
    """Log info message with correlation ID if available"""
    correlation_id = get_correlation_id()
    if correlation_id:
        message = f"[Correlation-ID: {correlation_id}] - " + message
    current_app.logger.info(message)


def logWarning(message: str):
    """Log warning message with correlation ID if available"""
    correlation_id = get_correlation_id()
    if correlation_id:
        message = f"[Correlation-ID: {correlation_id}] - " + message
    current_app.logger.warning(message)
