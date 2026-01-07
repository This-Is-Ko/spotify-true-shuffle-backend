from main import create_app
from __version__ import __version__

# Print application version at startup
print(f"True Shuffle Backend (Celery Worker) - Version {__version__}")

flask_app = create_app()
celery_app = flask_app.extensions["celery"]
