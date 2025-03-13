import pytest
from server import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_login_required_for_show_summary_get(client):
    response = client.get('/showSummary')
    assert response.status_code == 302


def test_login_required_for_book(client):
    response = client.get('/book/Spring%20Festival/Simply%20Lift')
    assert response.status_code == 302


def test_login_required_for_purchase_places(client):
    response = client.post('/purchasePlaces')
    assert response.status_code == 302


def test_login_not_required_for_points(client):
    response = client.get('/points')
    assert response.status_code == 200