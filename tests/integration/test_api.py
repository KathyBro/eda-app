from fastapi.testclient import TestClient
import pytest
from api.main import app


@pytest.fixture
def api_client():
    return TestClient(app)


def test_root__when_making_get__returns_hello_world(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
