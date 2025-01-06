import os
from dotenv import load_dotenv
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class
    """
    # Default settings
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False

    # Global applicable to all environments
    # Spotify settings
    SPOTIFY_CLIENT_ID = os.getenv(
        'SPOTIFY_CLIENT_ID', default='SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv(
        'SPOTIFY_CLIENT_SECRET', default='SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv(
        'SPOTIFY_REDIRECT_URI', default='SPOTIFY_REDIRECT_URI')

    # Cookies
    COOKIE_DOMAIN = os.getenv(
        'COOKIE_DOMAIN', default=None)

    # JWT
    JWT_SECRET = os.getenv(
        'JWT_SECRET', default='JWT_SECRET')
    JWT_ISSUER = os.getenv(
        'JWT_ISSUER', default='JWT_ISSUER')
    
    SERVICE_CLIENT_ID = os.getenv(
        'SERVICE_CLIENT_ID', default='SERVICE_CLIENT_ID')
    SERVICE_CLIENT_SECRET = os.getenv(
        'SERVICE_CLIENT_SECRET', default='SERVICE_CLIENT_SECRET')

    # CORS
    CORS_ORIGIN = os.getenv(
        'CORS_ORIGIN', default='http://localhost:3000')

    # Database
    MONGO_URI = os.getenv(
        'MONGO_URI', default='mongodb+srv://dbUser:password@cluster0.aa.mongodb.net/database?retryWrites=true&w=majority')
    
    # Celery
    CELERY_BROKER_URL = os.getenv(
        'CELERY_BROKER_URL', default='redis://localhost')
    CELERY_RESULT_BACKEND_URL = os.getenv(
        'CELERY_RESULT_BACKEND_URL', default='redis://localhost')

class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True


class TestingConfig(Config):
    FLASK_ENV = 'test'
    TESTING = True


class ProductionConfig(Config):
    FLASK_ENV = 'production'
