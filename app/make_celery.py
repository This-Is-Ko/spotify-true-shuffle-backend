from main import create_app
from __version__ import __version__
import logging

# Configure logging for Celery worker
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Log application version at startup
logger.info(f"True Shuffle Backend (Celery Worker) - Version {__version__}")

flask_app = create_app()
celery_app = flask_app.extensions["celery"]
