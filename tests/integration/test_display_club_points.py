import pytest
from server import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_display_club_points(client):
    response = client.get('/points')
    assert response.status_code == 200
    assert b'<h1>Club Points</h1>' in response.data
    assert b'<th>Club Name</th>' in response.data
    assert b'<th>Points</th>' in response.data