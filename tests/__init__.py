import pytest
from main import create_app


@pytest.fixture
def client():
    """Configures flask app for testing
    """
    test_app = create_app()

    # app.config['TESTING'] = True
    client = test_app.test_client()

    yield client
