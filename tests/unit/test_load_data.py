import pytest
from server import app, load_clubs, load_competitions


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_load_clubs(client):
    response = load_clubs()
    assert type(response) == list


def test_load_competitions(client):
    response = load_competitions()
    assert type(response) == list