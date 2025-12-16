
#external modules
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_session import Session

#python modules
from functools import wraps

#app imports
from app.data.db import get_database
from app.forms import SearchForm
from app.HaloData import *

#self
from . import content
from .services import fetchNewsBar, fetchSideBar 

##################
#-----Routes-----#
##################

@content.route('/', methods=["GET"])
def index():
    """ Home Page """
     
    videos = fetchSideBar() #set number to be retrieved
    news = fetchNewsBar() #set number to be retrieved

    return render_template('index.html', news=news, videos=videos)

#TODO: Report system
@content.route('/report', methods=['POST'])
def report():
    pass

#TODO: Fontend
@content.route('/search', methods=['GET', 'POST'])
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

#TODO: finish user profile (ADAM)
@content.route('/profile/<username>', methods=['GET', 'PATCH', 'DELETE'])
def profilePage(username):
    if request.method == "GET":
        logged_in_user = session.get('username')
        print(f"session username:", logged_in_user)

        if not logged_in_user:
            flash("you must be logged in to view your profile", "error")
            return redirect(url_for('content.index'))

        if username != logged_in_user:
            flash("sneaky! you can only view your own profile at the moment!", "error")
            return redirect(url_for('content.index'))
        
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

#TODO: Content
@content.route('/about', methods=['GET'])
def about_page():
    return render_template('about.html')

@content.route('/mapPage', methods=['GET'])
def mapsAll():
    return render_template('allmaps.html', HALO_3_DATA=HALO_3_DATA, GAME_MODES=GAME_MODES)

@content.route('/mapPage/<mapID>', methods=['GET'])
def mapPage(mapID):
    print(f'got request for: {mapID}')
    mapID = str(mapID).capitalize()
    maps_dict = HALO_INFINITE_DATA["Maps"]
    game_map = maps_dict.get(mapID)


    db = get_database()
    cur = db.cursor()

    #run query for allmap resources
    map_query =  """ 
    SELECT vidId, title, published, description, thumbnailshigh, thumbnailsmax, csr, gamemap, gamemode, videotype FROM Videos WHERE gamemap = ?
 
    """
    cur.execute(map_query, (mapID,))
    map_results = cur.fetchall()
    map_results = [dict(row) for row in map_results] #formats for JINJA2
     
    if not game_map:
        print(f'user attempted to access map variant: {mapID} but it doesnt exist. redirecting to siteError.HTML')
        return render_template('siteError.html')
    
    print(game_map)
    return render_template('map.html', map=game_map, GAME_MODES=GAME_MODES, map_results=map_results, infiniteCSR_Lookup=infiniteCSR_Lookup)
