import json
from flask import Flask,render_template,request,redirect,flash,url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


def load_clubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def load_competitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

competitions = load_competitions()
clubs = load_clubs()


class User(UserMixin):
    def __init__(self, name, email, points):
        self.id = email
        self.email = email
        self.name = name
        self.points = points


@login_manager.user_loader
def load_user(email):
    club = next((club for club in clubs if club['email'] == email), None)
    if club:
        return User(club['name'], email, club['points'])
    return None


@app.route('/')
def index():
    # If the user is already logged in, redirect to the show_summary page
    if current_user.is_authenticated:
        return redirect(url_for('show_summary_get'))

    return render_template('index.html')


@app.route('/show_summary',methods=['POST'])
def show_summary():
    try:
        email = request.form.get('email')
        club = [club for club in clubs if club['email'] == email][0]
        # If the email address is found in the clubs.json file, the user is logged in
        if club:
            login_user(load_user(email))
        next_url = request.form.get('next_page').removeprefix('/').split("/") if request.form.get('next_page') else None
        # If the next_page is not None, redirect to the next page
        if next_url:
            next_page = next_url[0]
            # If the next_page is 'book', redirect to the booking page
            if next_page == 'book':
                competition = next_url[1].replace('%20',' ')
                return redirect(url_for(next_page, competition=competition, club=club['name']))
            else:
                return redirect(url_for(next_page))
        return render_template('welcome.html',club=club,competitions=competitions)
    # If the email address is not found in the clubs.json file, the IndexError exception is raised
    except IndexError:
        flash('Sorry, this email address is not recognised')
        return redirect(url_for('index'))
    

@app.route('/show_summary',methods=['GET'])
@login_required
def show_summary_get():
    # Get the club details using the email address of the current user
    club = next((club for club in clubs if club['email'] == current_user.email), None)

    # If the club is not found, redirect to the index page
    if club is None:
        flash("Club not found")
        return redirect(url_for('index'))
    
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
@login_required
def book(competition,club):
    # Get the club details using the email address of the current user
    connected_club = next((club for club in clubs if club['email'] == current_user.id), None)
    # Check if the club name in the URL matches the club name of the current user
    if connected_club and club == connected_club['name']:
        foundCompetition = [c for c in competitions if c['name'] == competition][0]
        # If the club and competition are found, render the booking page
        if foundCompetition:
            return render_template('booking.html',club=connected_club,competition=foundCompetition)
        # If the club or competition is not found, redirect to the show_summary page
        else:
            flash("Something went wrong-please try again")
            return render_template('welcome.html', club=club, competitions=competitions)
    # If the club name in the URL does not match the club name of the current user, redirect to the show_summary page
    else:
        flash("You are not allowed to book for another club")
        return redirect(url_for('show_summary_get'))


@app.route('/purchase_places',methods=['POST'])
@login_required
def purchase_places():
    PLACE_LIMIT = 12
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    # Get the club details using the email address of the current user
    if club['email'] == current_user.id:
        # Check if the number of places requested is empty
        if not request.form['places']:
            flash('Sorry, you must enter a valid number of places')
            return redirect(url_for('show_summary_get'))
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
                flash(f'Great-booking complete! You have purchased {places_required} places for {competition["name"]}')
                
        return render_template('welcome.html', club=club, competitions=competitions)
    else:
        flash("You are not allowed to book for another club")
        return redirect(url_for('show_summary_get'))



# TODO: Add route for points display
@app.route('/points')
def points():
    return render_template('clubs_points.html',clubs=clubs)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404