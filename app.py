#Flask
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, g
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm, CSRFProtect

#Security
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

#Sessions
from flask_session import Session

#Forms
from wtforms import EmailField, PasswordField, StringField, SelectMultipleField, SelectField, SubmitField, IntegerField, widgets
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, Optional

#Databases
import sqlite3, os, hashlib, base64
from db import create_database

#internal imports
#=================
from extensions import app
from auth import log_in_user, register_user, recover_user, password_change
from HaloData import *
from formclasses import LoginForm, RegisterForm, SearchForm, RecoveryForm, PasswordResetForm, ArticleForm
from db import *
import db

#This route is called at the end of a request, removing db connection from g, ready for the next request
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#Inject required data for navbar
@app.context_processor
def inject_nav_data():
    return {
        "HALO_INFINITE_DATA": HALO_INFINITE_DATA
    }


# Routes

# Home Page
#===================
@app.route('/')
def index():
    if not session.get("name"):
        print(session)
    print(session)
    return render_template('home.html', title="Vanadam Halo")


# Admin dashboard
#===================
@app.route('/staff/<admintoken>')
def staff_login(admintoken):
    pass 

#Registration & Validation
#===================
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # If already logged in, do not show login page (commented out request.method =="GET" and)
    if 'username' in session:
        flash("Cannot log in while already logged in.", "error")
        return redirect(url_for('index'))

    # Handle Login
    if request.method == "POST":
        if log_in_user(form):
            flash(f"Logged in as {session['username']}", "success")
            return redirect(url_for('index'))
        else:
            flash("Incorrect username or password.", "error")
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)



@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('logged_in', None)

    flash("You’ve been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm()

    if request.method == "GET" and 'username' in session:
            print("Already logged in")
            flash("Cannot register a new account while already logged in.", "error")   
            return redirect(url_for('index'))
    
    if request.method == "POST":
        if register_user(form): # Retrieve inputs from form
            flash("Registration Successful", "success")          
            return redirect(url_for('index'))
        
        else:    
            flash("Credentials already taken", "error")
            return redirect(url_for('register'))
        
    return render_template('register.html', form=form)


@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    form = RecoveryForm()

    if request.method == "GET":  
            return render_template('recovery.html', form=form)
    
    if request.method == "POST":
        if form.validate_on_submit():
            recover_user(form)
            return redirect(url_for('index'))
           
    return render_template('home.html')



@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    
    form = PasswordResetForm()

    if request.method == 'GET':
        return render_template('reset_password.html', token=token, form=form)
    
    elif request.method == 'POST':
        if password_change(form):
            log_in_user(form)
            flash(f"password changed successfully. Logged in as {form.username.data}")
            return redirect(url_for('index'))
    else:
        flash('A recovery error has occured', 'error')
        return render_template('siteerror.html')
    


#===================
#Content
@app.route('/article', methods=['GET', 'PATCH', 'POST', 'DELETE'])
def article():
    pass

@app.route('/article/create', methods=['GET', 'POST'])
def article_create():
    form = ArticleForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        tags = form.tags.data

        db = get_database()
        cur = db.cursor()

        query = "INSERT INTO Articles (title, content, tags) VALUES (?, ?, ?)"
        cur.execute(query, (title, content, tags))
        db.commit()

        print("Article Created")
    return render_template('article_create.html')

@app.route('/article/<id>/edit', methods=['GET', 'PATCH', 'POST', 'DELETE'])
def article_edit():
    form = ArticleForm()
    return render_template('article_edit.html')

@app.route('/info/<infoType>', methods=['GET'])
def infoPages(infoType):
    # coaching, get involved, etc. not sure if should all have endpoints... (discuss?)
    pass

@app.route('/mapPage', methods=['GET'])
def mapsAll():
    return render_template('allmaps.html', HALO_3_DATA=HALO_3_DATA, GAME_MODES=GAME_MODES)

@app.route('/mapPage/<mapID>', methods=['GET'])
def mapPage(mapID):
    print(f'got request for: {mapID}')
    mapID = str(mapID).capitalize()
    maps_dict = HALO_INFINITE_DATA["Maps"]
    game_map = maps_dict.get(mapID)


    db = get_database()
    cur = db.cursor()

    #run query for allmap resources
    map_query =  """ 
    SELECT vidId, title, published, thumbnailsmax, thumbnailshigh, csr, map, gamemode, videotype, videocategory FROM Videos WHERE map = ?
 
    """
    cur.execute(map_query, (mapID,))
    map_results = cur.fetchall()
    map_results = [dict(row) for row in map_results] #formats for JINJA2
    
    if not game_map:
        print(f'user attempted to access map variant: {mapID} but it doesnt exist. redirecting to siteError.HTML')
        return render_template('siteError.html')
    
    print(game_map)
    return render_template('map.html', map=game_map, GAME_MODES=GAME_MODES, map_results=map_results, infiniteCSR_Lookup=infiniteCSR_Lookup)

@app.route('/profile/<username>', methods=['GET', 'PATCH', 'DELETE'])
def profilePage(username):
    if request.method == "GET":
        logged_in_user = session.get('username')
        print(f"session username:", logged_in_user)

        if not logged_in_user:
            flash("you must be logged in to view your profile", "error")
            return redirect(url_for('index'))

        if username != logged_in_user:
            flash("sneaky! you can only view your own profile at the moment!", "error")
            return redirect(url_for('index'))
        
        print(f"got request to load profile page for: {logged_in_user}")
        return render_template('profile.html', username=logged_in_user)

"""
    if request.method == "PATCH" and logged_in_user == username:
        form = ProfileEditForm()
        enter_db()

    if form.validate_on_submit():  # If form passes validation rules
        # Retrieve inputs from form
        username = form.username.data
        email = form.email.data
        password = form.password.data
        password2 = form.password2.data
        print("RegisterForm has been validated")
        if password != password2:
            flash("Passwords don't match!", "error")
            return render_template('register.html', form=form)

        query = "SELECT * FROM Users WHERE username = ? OR email = ?"
        cur.execute(query, (username, email))
        existing_user = cur.fetchone()

        if existing_user is None:
            flash("An account with those details doesnt exist", "error")
            return redirect(url_for('recovery'))

        if existing_user:
"""

@app.route('/report', methods=['POST'])
def report():
    pass


# TAG FILTERING WILL NEED REWORKING, Maybe use JSON
@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        # Extract form data variables
        #General Filters
        date = form.date.data
        if date is None:
            #date=todaysdate
            pass
        date_selector = form.date_selector.data #Determines wether to search for posts before, after or on given date

        tags = form.tags.data #Array of tags

        #Blog filters
        original_poster = form.original_poster.data

        #Video Filters
        vid_type = form.vid_type.data
        selected_games = form.games.data #Array of games
        selected_maps = form.maps.data #Array of maps
        gamemode = form.gamemode.data
        
        min_mmr = form.min_mmr.data
        if min_mmr is None:
            min_mmr = 0
        max_mmr = form.max_mmr.data
        if max_mmr is None:
            max_mmr = 9999

        # Print for debugging
        print("Date:", date)
        print("Date Selector:", date_selector)

        print("Tags:", tags)

        print("Original Poster:", original_poster)
        print("Video Type:", vid_type)
        print("Selected Games:", selected_games)
        print("Selected Maps:", selected_maps)
        print("Game Mode:", gamemode)
        print("Min MMR:", min_mmr)
        print("Max MMR:", max_mmr)

        db = get_database()
        cur = db.cursor()

        #SQL, filters are applied as needed, with conditions and parameters being put into respective lists and
        #concatenated into query
        query = "SELECT * FROM Posts"
        conditions = []
        params = []

        # DATE FILTERS
        if date_selector == 'On':
            conditions.append("date = ?")
            params.append(date)

        elif date_selector == 'Before':
            conditions.append("date < ?")
            params.append(date)

        elif date_selector == 'After':
            conditions.append("date > ?")
            params.append(date)

        # TAGS WILL NEED REWORKING, JSONIFY?
        if tags:
            conditions.append("tags = ?")
            params.append(tags)

        # ORIGINAL POSTER
        if original_poster:
            conditions.append("original_poster = ?")
            params.append(original_poster)

        # VIDEO TYPE
        if vid_type:
            conditions.append("video_type = ?")
            params.append(vid_type)

        # SELECTED GAMES (list)
        if selected_games:
            placeholders = ",".join("?" for _ in selected_games) #iterate through selected_games list, join them. comma-seperated
            conditions.append(f"game IN ({placeholders})")       #
            params.extend(selected_games)

        # SELECTED MAPS (list)
        if selected_maps:
            placeholders = ",".join("?" for _ in selected_maps)
            conditions.append(f"map IN ({placeholders})")
            params.extend(selected_maps)

        # GAME MODE
        if gamemode:
            conditions.append("gamemode = ?")
            params.append(gamemode)

        # MMR RANGE
        if min_mmr is not None:
            conditions.append("mmr >= ?")
            params.append(min_mmr)

        if max_mmr is not None:
            conditions.append("mmr <= ?")
            params.append(max_mmr)

        # Combine WHERE if any conditions exist
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        print("Final Query:", query)
        print("Params:", params)

        # Execute
        cur.execute(query, params)
        result = cur.fetchall()
    return render_template('search.html', form=form)

@app.route('/videos/<videoID>', methods=['GET'])
def video(videoID):
    pass

# Run application
#=========================================================
# This code executes when the script is run directly.
if __name__ == '__main__':
    print("Starting Flask application...")
    print("Open Your Application in Your Browser: http://localhost:81")
    # The app will run on port 81, accessible from any local IP address
    app.run(host='0.0.0.0', port=81)
