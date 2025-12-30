
import pytest
from cost_sharing.app import create_app


@pytest.fixture(name='client')
def create_client():
    app = create_app()
    return app.test_client()

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "Hello, World!"
