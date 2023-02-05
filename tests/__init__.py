import pytest
from main import create_app
from flask import Flask
from unittest.mock import patch
import os


@pytest.fixture
def client():
    """Configures flask app for testing
    """
    test_app = create_app()

    client = test_app.test_client()

    yield client


@pytest.fixture
@patch.dict(os.environ, {"COUNTER_DIRECTORY": "./counters"})
@patch.dict(os.environ, {"SPOTIFY_CLIENT_ID": "1111111111111"})
@patch.dict(os.environ, {"SPOTIFY_CLIENT_SECRET": "222222222222"})
@patch.dict(os.environ, {"SPOTIFY_REDIRECT_URI": "http://localhost:3000"})
@patch.dict(os.environ, {"MONGO_URI": "mongodb+srv://MONGO_URI"})
def env_patch():
    return
