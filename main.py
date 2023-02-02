from flask import Flask
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__)
    cors = CORS(app)

    # Select env and set up config
    CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object("config." + CONFIG_TYPE)

    # Register blueprints for app
    register_all_blueprints(app)

    return app


def register_all_blueprints(app):
    from controllers.spotify_auth_controller import spotify_auth_controller
    from controllers.spotify_playlist_controller import spotify_playlist_controller
    from controllers.shuffle_controller import shuffle_controller
    from controllers.statistics_controller import statistics_controller

    app.register_blueprint(spotify_auth_controller)
    app.register_blueprint(spotify_playlist_controller)
    app.register_blueprint(shuffle_controller)
    app.register_blueprint(statistics_controller)
