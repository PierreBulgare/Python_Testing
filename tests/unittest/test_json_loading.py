from server import loadClubs, loadCompetitions


def test_loadClubs():
    """Teste si la fonction loadClubs retourne une liste"""
    assert isinstance(loadClubs(), list)


def test_loadCompetitions():
    """Teste si la fonction loadCompetitions retourne une liste"""
    assert isinstance(loadCompetitions(), list)