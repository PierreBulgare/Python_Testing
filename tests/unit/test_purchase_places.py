import pytest
from server import app
from flask_login import login_user
from server import User

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


def mock_clubs(points=13):
    return [
        {
            "name": "Simply Lift",
            "email": "john@simplylift.co",
            "points": points
        }
    ]


def mock_competitions(status):
    if status == 'fully_booked':
        return [
            {
                "name": "Spring Festival",
                "numberOfPlaces": 0
            }
        ]

    if status == 'club_places_full':
        return [
            {
                "name": "Spring Festival",
                "numberOfPlaces": 12,
                "clubs": {
                    "Simply Lift": {
                        "places": 12
                    }
                }
            }
        ]
    

def test_logged_in_session(logged_in_client):
    """Vérifie que l'utilisateur est bien connecté"""
    with logged_in_client.session_transaction() as sess:
        assert '_user_id' in sess, "L'utilisateur n'est pas connecté"
        assert sess['_user_id'] == "john@simplylift.co", f"ID utilisateur attendu: 'john@simplylift.co', reçu: {sess['_user_id']}"


def test_places_required_exceeds_limit(logged_in_client):
    """Test that the number of places requested exceeds the limit of 12"""
    response = logged_in_client.post('/purchase_places', data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '13'})
    assert b"Sorry, you can only purchase up to 12 places" in response.data


def test_places_required_less_than_one(logged_in_client):
    """Test that the number of places requested is less than or equal to 0"""
    response = logged_in_client.post('/purchase_places', data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '0'})
    assert b"Sorry, you must purchase at least 1 place" in response.data


def test_not_enough_competition_places(logged_in_client):
    """Test that there are not enough places left in the competition based on the request"""
    response = logged_in_client.post('/purchase_places', data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '100'})
    assert b"Sorry, there are not enough places left in this competition based on your request" in response.data


def test_not_enough_club_points(logged_in_client, mocker):
    """Test that the club does not have enough points to purchase the required places"""
    mocker.patch('server.clubs', mock_clubs(points=10))
    
    response = logged_in_client.post('/purchase_places', data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '12'})
    assert b"Sorry, you do not have enough points to purchase this many places" in response.data


def test_competition_fully_booked(logged_in_client, mocker):
    """Test that the competition is fully booked"""
    mocker.patch('server.clubs', mock_clubs())
    mocker.patch('server.competitions', mock_competitions(status='fully_booked'))

    response = logged_in_client.post('/purchase_places', data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '1'})
    assert b"Sorry, this competition is already fully booked" in response.data


def test_club_reaches_limit(logged_in_client, mocker):
    """Test that the club reaches the limit of 12 places after booking"""
    mocker.patch('server.clubs', mock_clubs())
    mocker.patch('server.competitions', mock_competitions(status='club_places_full'))

    response = logged_in_client.post('/purchase_places', data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '1'})
    assert b"Sorry, only 12 places are allowed per club" in response.data


def test_booking_complete(logged_in_client):
    """Test that the booking is complete"""
    response = logged_in_client.post('/purchase_places', data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '1'})
    assert b"Great-booking complete!" in response.data
