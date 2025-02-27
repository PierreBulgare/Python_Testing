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
    except IndexError:
        flash('Club not found')
        return redirect(url_for('index'))
    return render_template('welcome.html',club=club,competitions=competitions)


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
    PLACES_LIMIT = 12

    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])

    # Check if the competition is full
    if int(competition['numberOfPlaces']) == 0:
        flash('Sorry, competition is full')
        return render_template('welcome.html', club=club, competitions=competitions)

    # Check if the number of places requested does not exceed the limit
    if placesRequired > PLACES_LIMIT:
        flash(f'Sorry, you cannot book more than {PLACES_LIMIT} places')
        return render_template('welcome.html', club=club, competitions=competitions)

    # Check if the club has enough points
    if int(club['points']) < placesRequired:
        flash('Sorry, you do not have enough points')
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # Check if there are enough places available
    if placesRequired > int(competition['numberOfPlaces']):
        flash('Sorry, not enough places available')
        return render_template('welcome.html', club=club, competitions=competitions)

    # Update the number of places available
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired

    # Update the club's points
    club['points'] = int(club['points'])-placesRequired

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))