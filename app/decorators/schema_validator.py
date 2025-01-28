from functools import wraps
from flask import current_app, request
from marshmallow import ValidationError

def validate_request_schema(schema_class):
    """
    A decorator to validate the request body against a given schema.
    Passes the validated data as `request_body` to the decorated function.

    Args:
        schema_class (class): The Marshmallow schema class to validate against.
        
    Returns:
        function: The decorated function with `request_body` passed as a keyword argument.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                current_app.logger.debug("Validating request body")
                request_data = request.get_json()
                schema = schema_class()
                request_body = schema.load(request_data)
            except ValidationError as e:
                current_app.logger.error("Invalid request: " + str(e.messages))
                return {"error": "Invalid request"}, 400
            except Exception as e:
                current_app.logger.error("Invalid request: " + str(e))
                return {"error": "Invalid request"}, 400

            # Pass validated data to the decorated function
            return f(*args, request_body=request_body, **kwargs)
        return decorated
    return decorator