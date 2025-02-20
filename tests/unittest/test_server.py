from server import app


class TestServer:
    """Teste les routes de l'application"""
    def test_index(self):
        """Teste la route index"""
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            assert b'Welcome to the GUDLFT Registration Portal!' in response.data

    def test_showSummary(self):
        """Teste la route showSummary"""
        email = 'john@simplylift.co'
        with app.test_client() as client:
            response = client.post('/showSummary',
                                   data={'email': email})
            assert response.status_code == 200
            assert b'Summary | GUDLFT Registration' in response.data

    def test_book(self):
        """Teste la route book"""
        club = 'Simply Lift'
        competition = 'Spring Festival'
        with app.test_client() as client:
            response = client.get(f'/book/{competition}/{club}')
            assert response.status_code == 200
            assert b'Booking for' in response.data

    def test_purchasePlaces(self):
        """Teste la route purchasePlaces"""
        club = 'Simply Lift'
        competition = 'Spring Festival'
        places = 2
        with app.test_client() as client:
            response = client.post('/purchasePlaces',
                                   data={'club': club,
                                         'competition': competition,
                                         'places': places})
            assert response.status_code == 200
            assert b'Great-booking complete!' in response.data

    def test_logout(self):
        """Teste la route logout"""
        with app.test_client() as client:
            response = client.get('/logout')
            assert response.status_code == 302
            assert response.headers['Location'] == '/'
