from flask import current_app

from exceptions.custom_exceptions import AccessTokenInvalid


def validate_cron_api_key(request):
    """Validate X-Cron-Key header against configured CRON_API_KEY"""
    api_key = request.headers.get('X-Cron-Key')
    expected_key = current_app.config.get("CRON_API_KEY")

    if not expected_key:
        raise AccessTokenInvalid("Cron API key not configured")
    if not api_key or api_key != expected_key:
        raise AccessTokenInvalid("Invalid cron API key")

