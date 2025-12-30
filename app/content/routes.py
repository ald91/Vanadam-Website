#TODO: BUG : when a user changes their username the flash message for user not logged in occurs. (check redirect?)

#external modules
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_session import Session

#python modules
from functools import wraps

#app imports
from app.services import Post_Form_Match_Case
from app.forms import SearchForm
from app.HaloData import *
from app.forms import CoachingForm, ProfileEditForm, YouTubeReviewForm


#db imports
from app.data.db import get_database
from app.data.db_services_users import User_Profile_Update, Single_User_Query
from app.data.db_services_coaching import Register_New_Coaching_Request, Coaching_Save_JSON, Register_New_YT_Request, Coaching_Record_Modify_Quick, YT_Record_Modify_Quick, Coaching_Query,  Youtube_Query
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

@content.route('/profile/<int:userID>', methods=['GET', 'POST'])
def profilePage(userID):
    
    username:str = session.get('username')
    userID:int = session.get('userID')

    if session['username'] == None and session['userID'] == None:
            flash("you must be logged in to view your profile", "danger")
            return redirect(url_for('content.index'))         
    
    elif request.method == 'GET':
        userData = Single_User_Query("self", userID)
        userCrequests= Coaching_Query("self", userID=session["userID"])
        userYTrequests = Youtube_Query("self", userID=session["userID"])

    elif request.method == 'POST':
        print(Post_Form_Match_Case(request.form.get("userprofile")))
        matchCase = Post_Form_Match_Case(request.form.get("userprofile"))
        print(matchCase)
        action = matchCase[0]
        requestID = matchCase[1]

        match action:
            case "edit_profile":
                return redirect(url_for("content.User_Self_Edit_Profile", username=username))
            case "delete_crequest":
                flag = Coaching_Record_Modify_Quick(requestID, action="delete")
            case "delete_YTrequest":
                flag = YT_Record_Modify_Quick(requestID, action="delete")
            case _:
                flag = None

        if flag:
            flash(f"succesfully carried out {action} on {requestID}", "success")
        elif not flag:
            flash(f"couldnt complete request to action: ({action}) on item with request ID: ({requestID})", "warning")
        else:
            flash("unknown request", "error")
    
        return redirect(url_for('content.profilePage', userID=userID))

    return render_template('profile.html', username=username, userID=userID , userData=userData, userCrequests=userCrequests, userYTrequests=userYTrequests)

@content.route('/profile/edit/<userID>', methods=['GET', 'POST'])
def User_Self_Edit_Profile(userID):

    userID = session.get('userID')
    username = session.get('username')
    userData = Single_User_Query("self", userID)
    profile_form = ProfileEditForm()

    if username != userData.get('username') and userID != userData.get('userID'):
            flash("Naughty! trying to edit someone elses profile!", "danger")
            return redirect(url_for('content.index'))    
    
    elif request.method == "GET":
        profile_form.username.data = userData["username"]
        profile_form.email.data = userData["email"]
        profile_form.xboxname.data = userData["xboxname"]
        profile_form.timezone.data = userData["timezone"]
        profile_form.arenarank.data = userData["arenarank"]

    elif request.method == "POST":
        if profile_form.validate_on_submit():
            # Only proceed if the user clicked the correct submit button
            flag = User_Profile_Update(userID, profile_form)
            if flag:
                flash("Your profile has been updated. Refresh the page if changes are not visible.", "success")
            else:
                flash("Your profile could not be updated. If this happens again, contact admin.", "warning")       
        else:
            flash("form data invalid", "warning")
        
        return redirect(url_for("content.profilePage", userID=userID))
        
    return render_template("profile_edit.html", ProfileForm=profile_form, userID=userID)

@content.route('/about', methods=['GET'])
def about_page():
    return render_template('about.html')

@content.route('/YT-Request', methods=['GET', 'POST'])
def youtube_request():

    form = YouTubeReviewForm()
    if not session["username"] and not session["userID"]:
        flash("you need a user account to submit videos for Youtube Review, please register an account", "information")

    elif session["userID"] and request.method == 'GET':
        print(session["userID"])
        userData = Single_User_Query(userID=session["userID"])
        print(userData)
        form.username.data = userData.get("username")
        form.xboxname.data = userData.get("xboxname") or None
        form.arenarank.data = userData.get("arenarank") or None
        return render_template('ytrequests.html', form=form)
    
    elif request.method == 'POST':
        form.validate_on_submit()
        action = Register_New_YT_Request(form, session["userID"])
        if action:
            flash("request successfully registered, check your profile for it's progress", "success")
            return redirect(url_for('content.index'))
        if not action:
            flash("your reuqest had a problem, please try again", "warning")
            return redirect(url_for('content.youtube_request'))

    else:
        return render_template('ytrequests.html', form=form)
    
    flash("unknown request handled", "warning")
    return render_template('ytrequests.html', form=form)

@content.route('/coaching', methods=['GET', 'POST'])
def coaching():
    
    form = CoachingForm()
    userData = {"" : ""}
    
    if request.method == 'POST':
        if form.validate_on_submit():
            coachingRequest = Register_New_Coaching_Request(form)
            if coachingRequest:
                flash("thank you for submitting your request, it is now on your profile where you can see it's progress", "success")
                return redirect(url_for('content.index'))
            else:
                flash("there was an issue with your submission, please try again. If this persists, contact an admin", "warning")
                return redirect(url_for('content.coaching'))

    else:
        #backfill user data if they're logged in UX :)
        if session.get('userID'):
            userData = Single_User_Query("self", session.get('userID'))
            form.timezone.data = userData["timezone"]
            form.username.data = userData["username"]
            form.email.data = userData["email"]
            form.xboxname.data = userData["xboxname"]
            form.arenarank.data = userData["arenarank"]

        return render_template('coaching.html', form=form, userData=userData)

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
