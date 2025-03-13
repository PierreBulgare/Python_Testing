import pytest
from server import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def login(client, email):
    """Fonction utilitaire pour simuler une connexion."""
    return client.post('/showSummary', data={'email': email})


def test_index(client):
    """Test que la page d'accueil renvoie un code 200."""
    response = client.get('/')
    assert response.status_code == 200


def test_showSummary(client):
    """Test que la connexion fonctionne avec un email valide."""
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200


def test_showSummary_not_found(client):
    """Test que la connexion avec un email inconnu redirige (302)."""
    response = login(client, 'john@simplylift.com')
    assert response.status_code == 302


def test_book(client):
    """Test que la réservation renvoie un code 200."""
    login(client, 'john@simplylift.co')
    response = client.get('/book/Spring%20Festival/Simply%20Lift')
    assert response.status_code == 200


def test_book_without_competition_and_club(client):
    """Test que la réservation échoue si la compétition ou le club n'existe pas."""
    login(client, 'john@simplylift.com')
    response = client.get('/book')
    assert response.status_code == 404


def test_book_without_competition_or_club(client):
    """Test que la réservation échoue si la compétition ou le club n'existe pas."""
    login(client, 'john@simplylift.com')
    response = client.get('/book/Spring Festival')
    assert response.status_code == 404


def test_logout(client):
    """Test que la déconnexion redirige correctement."""
    login(client, 'john@simplylift.com')
    response = client.get('/logout')
    assert response.status_code == 302


def test_page_not_found(client):
    """Test qu'une page inconnue renvoie une erreur 404."""
    response = client.get('/nonexistentpage')
    assert response.status_code == 404
