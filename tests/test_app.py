import pytest
from oauth_handler_stub import OAuthHandlerStub
from cost_sharing.app import create_app
from cost_sharing.storage import InMemoryCostStorage
from cost_sharing.cost_sharing import CostSharing


@pytest.fixture(name='client')
def create_client():
    """Create Flask test client with stubbed dependencies."""
    # Create stub oauth_handler
    oauth_handler = OAuthHandlerStub()

    # Create real storage and application instances for testing
    storage = InMemoryCostStorage()
    application = CostSharing(storage)

    app = create_app(oauth_handler, application)
    return app.test_client()


def test_index(client):
    """Test that index route returns Hello, World!"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "Hello, World!"
