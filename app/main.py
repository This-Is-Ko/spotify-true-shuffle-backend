from flask import Flask
from flask_cors import CORS
import os
from flask_pymongo import PyMongo
from celery import Celery, Task
import logging
import faulthandler

mongo = PyMongo()


def create_app():
    app = Flask(__name__)

    # Configure logging level and format
    logging.basicConfig(level=logging.INFO)
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)

    faulthandler.enable()

    # Select env and set up config
    CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object("config." + CONFIG_TYPE)
    app.logger.info("Config set up for " + CONFIG_TYPE)

    # Enable CORS
    CORS(app, supports_credentials=True, origins=[app.config["CORS_ORIGIN"]])

    # Register blueprints for app
    register_all_blueprints(app)

    # Initialise mongodb client
    try:
        mongo.init_app(app)
    except Exception:
        """We don't provide a URI when running unit tests, so PyMongo will fail to initialize.
        This is okay because we replace it with a version for testing anyway. """
        app.logger.info('PyMongo not initialized!')

    app.config.from_mapping(
        CELERY=dict(
            broker_url=app.config["CELERY_BROKER_URL"],
            result_backend=app.config["CELERY_RESULT_BACKEND_URL"],
            task_ignore_result=True,
            broker_connection_retry_on_startup=True
        ),
    )
    celery_init_app(app)

    return app


def register_all_blueprints(app):
    from controllers.spotify_auth_controller import spotify_auth_controller
    from controllers.playlist_controller import playlist_controller
    from controllers.statistics_controller import statistics_controller
    from controllers.trackers_controller import trackers_controller
    from controllers.user_controller import user_controller
    from controllers.auth_controller import auth_controller
    from controllers.session_controller import session_controller

    app.register_blueprint(spotify_auth_controller)
    app.register_blueprint(playlist_controller)
    app.register_blueprint(statistics_controller)
    app.register_blueprint(trackers_controller)
    app.register_blueprint(user_controller)
    app.register_blueprint(auth_controller)
    app.register_blueprint(session_controller)


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.Task = FlaskTask
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


app = create_app()
