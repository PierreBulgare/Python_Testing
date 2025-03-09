import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        return render_template('welcome.html',club=club,competitions=competitions)
    # If the email address is not found in the clubs.json file, the IndexError exception is raised
    except IndexError:
        flash('Sorry, this email address is not recognised')
        return redirect(url_for('index'))

@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    PLACE_LIMIT = 12
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    places_required = int(request.form['places'])
    competition_places = int(competition['numberOfPlaces'])
    club_points = int(club['points'])

    # If the competition does not have a 'clubs' key, create one
    if not competition.get('clubs'):
        competition['clubs'] = {}

    # Check if the number of places requested is less than or equal to 0
    if places_required <= 0:
        flash('Sorry, you must purchase at least 1 place')

    # Check if the competition is already fully booked
    elif competition_places <= 0:
        flash('Sorry, this competition is already fully booked')

    # Check if the number of places requested is more than the number of places left in the competition
    elif places_required > competition_places:
        flash('Sorry, there are not enough places left in this competition based on your request')

    # Check if the number of places requested is more than the limit
    elif places_required > PLACE_LIMIT:
        flash('Sorry, you can only purchase up to 12 places')

    # Check if the number of places requested is more than the number of points
    elif places_required > club_points:
        flash('Sorry, you do not have enough points to purchase this many places')

    # If all the checks pass, update the number of points and places left
    else:
        # If the club is not in the competition, add it
        if not competition['clubs'].get(club['name']):
            competition['clubs'][club['name']] = { 'places': 0 }

        # Check if the club will reach the limit of 12 places after booking
        if competition['clubs'][club['name']]['places'] + places_required > PLACE_LIMIT:
            flash('Sorry, only 12 places are allowed per club')
        else:
            # Update the number of places left for the competition
            competition['numberOfPlaces'] = competition_places - places_required
            # Update the number of points left for the club
            club['points'] = club_points - places_required
            # Update the number of places booked by the club for the competition
            competition['clubs'][club['name']]['places'] += places_required
            flash('Great-booking complete!')

    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display
@app.route('/points')
def points():
    return render_template('clubs_points.html',clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404