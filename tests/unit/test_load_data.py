import pytest
from server import app, loadClubs, loadCompetitions


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_loadClubs(client):
    response = loadClubs()
    assert type(response) == list


def test_loadCompetitions(client):
    response = loadCompetitions()
    assert type(response) == list