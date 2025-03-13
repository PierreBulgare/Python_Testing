import pytest
from server import app, User
from flask_login import login_user


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def logged_in_client(client, mocker):
    """Connecte un utilisateur en session Flask-Login"""
    club = User("Simply Lift", "john@simplylift.co", 13)
    mocker.patch('server.load_user', return_value=club)  # Mocke la fonction load_user

    with client.session_transaction() as sess:
        sess['_user_id'] = club.id  # Stocke l'ID utilisateur dans la session

    with app.test_request_context():  # Création d'un contexte de requête Flask
        login_user(club)  # Connexion effective de l'utilisateur

    return client


def test_empty_email(client):
    response = client.post('/show_summary', data={'email': ''})
    assert response.status_code == 302


def test_empty_places(logged_in_client):
    response = logged_in_client.post('/purchase_places', data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': ''})
    assert response.status_code == 302