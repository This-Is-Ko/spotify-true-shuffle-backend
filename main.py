from flask import Flask
from flask_cors import CORS
import os
from flask_pymongo import PyMongo

mongo = PyMongo()


def create_app():
    app = Flask(__name__)

    # Select env and set up config
    CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object("config." + CONFIG_TYPE)
    app.logger.info("Config set up for " + CONFIG_TYPE)

    # Enable CORS
    cors = CORS(app, supports_credentials=True,
                origins=app.config["CORS_ORIGIN"])

    # Register blueprints for app
    register_all_blueprints(app)

    # Initialise mongodb client

    try:
        mongo.init_app(app)
    except:
        """We don't provide a URI when running unit tests, so PyMongo will fail to initialize.
        This is okay because we replace it with a version for testing anyway. """
        app.logger.info('PyMongo not initialized!')

    return app


def register_all_blueprints(app):
    from controllers.spotify_auth_controller import spotify_auth_controller
    from controllers.playlist_controller import playlist_controller
    from controllers.statistics_controller import statistics_controller
    from controllers.trackers_controller import trackers_controller
    from controllers.user_controller import user_controller
    from controllers.auth_controller import auth_controller

    app.register_blueprint(spotify_auth_controller)
    app.register_blueprint(playlist_controller)
    app.register_blueprint(statistics_controller)
    app.register_blueprint(trackers_controller)
    app.register_blueprint(user_controller)
    app.register_blueprint(auth_controller)


app = create_app()
