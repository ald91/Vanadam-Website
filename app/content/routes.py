#external modules
from flask import render_template, redirect, url_for, flash, request, session
from flask_session import Session

#python modules
from functools import wraps

#app imports
from app.services import post_form_match_case
from app.forms import SearchForm
from app.HaloData import *
from app.forms import CoachingForm, ProfileEditForm, YouTubeReviewForm


#db imports
from app.data.db import get_database
from app.data.db_services_users import User_Profile_Update, Single_User_Query
from app.data.db_services_coaching import register_new_coaching_request, coaching_save_JSON, register_new_YT_request, coaching_record_modify_quick, YT_record_modify_quick, coaching_query,  youtube_query
#self
from . import content
from .services import fetchNewsBar, fetchSideBar , process_search

##################
#-----Routes-----#
##################

@content.route('/', methods=["GET"])
def index():
    """ Home Page """
     
    videos = fetchSideBar() #set number to be retrieved
    news = fetchNewsBar() #set number to be retrieved

    return render_template('index.html', news=news, videos=videos)

#TODO: Fontend
@content.route('/search', methods=['GET', 'POST'])
def search():
    """Retrieve params from form, package into dict to be sent to search_results for processing"""
    form = SearchForm()

    if form.validate_on_submit():

        search_params = {
            "date": form.date.data.isoformat() if form.date.data else None,
            "date_selector": form.date_selector.data,
            "tags": form.tags.data,
            "vid_type": form.vid_type.data,
            "gamemode": form.gamemode.data,
            "min_csr": form.min_csr.data,
            "max_csr": form.max_csr.data,
            "maps": form.maps.data
        }
        #Strip empty values
        search_params = {
            k: v for k, v in search_params.items()
            if v not in (None, "", [])
        }

        return redirect(url_for("content.results", **search_params))

    return render_template("search.html", form=form)

@content.route('/search/results')
def results():
    search_results = process_search()
    return render_template("results.html", search_results=search_results, infiniteCSR_Lookup=infiniteCSR_Lookup, GAME_MODES=GAME_MODES)


@content.route('/profile/<int:userID>', methods=['GET', 'POST'])
def profile_page(userID):
    """ renders user profile, if user has active session"""
    username:str = session.get('username')
    userID:int = session.get('userID')

    if session['username'] is None and session['userID'] is None:
        flash("you must be logged in to view your profile", "danger")
        return redirect(url_for('content.index'))           
    elif request.method == 'GET':
        user_data = Single_User_Query("self", userID) or None
        user_crequests= coaching_query("self", userID=session["userID"]) or None
        user_YTrequests = youtube_query("self", userID=session["userID"]) or None
    elif request.method == 'POST':
        print(post_form_match_case(request.form.get("userprofile")))
        match_case = post_form_match_case(request.form.get("userprofile"))
        print(match_case)
        action = match_case[0]
        requestID = match_case[1]

        match action:
            case "edit_profile":
                return redirect(url_for("content.user_self_edit_profile", username=username))
            case "delete_crequest":
                flag = coaching_record_modify_quick(requestID, action="delete")
            case "delete_YTrequest":
                flag = YT_record_modify_quick(requestID, action="delete")
            case _:
                flag = None

        if flag:
            flash(f"succesfully carried out {action} on {requestID}", "success")
        elif not flag:
            flash(f"couldnt complete request to action: ({action}) on item with request ID: ({requestID})", "warning")
        else:
            flash("unknown request", "error")
    
        return redirect(url_for('content.profile_page', userID=userID))

    return render_template('profile.html', username=username, userID=userID , user_data=user_data, user_crequests=user_crequests, user_YTrequests=user_YTrequests)

@content.route('/profile/edit/<userID>', methods=['GET', 'POST'])
def user_self_edit_profile(userID):
    """ allows user to edit their profile, requires signed in"""
    userID = session.get('userID')
    username = session.get('username')
    user_data = Single_User_Query("self", userID)
    profile_form = ProfileEditForm()

    if username != user_data.get('username') and userID != user_data.get('userID'):
            flash("Naughty! trying to edit someone elses profile!", "danger")
            return redirect(url_for('content.index'))    
    
    elif request.method == "GET":
        profile_form.username.data = user_data["username"]
        profile_form.email.data = user_data["email"]
        profile_form.xboxname.data = user_data["xboxname"]
        profile_form.timezone.data = user_data["timezone"]
        profile_form.arenarank.data = user_data["arenarank"]

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
        
        return redirect(url_for("content.profile_page", userID=userID))
        
    return render_template("profile_edit.html", ProfileForm=profile_form, userID=userID)

@content.route('/about', methods=['GET'])
def about_page():
    """ simple about page GET."""
    return render_template('about.html')

@content.route('/YT-Request', methods=['GET', 'POST'])
def youtube_request():
    """ allows users to submit a YouTube request"""
    form = YouTubeReviewForm()
    if not session["username"] and not session["userID"]:
        flash("you need a user account to submit videos for Youtube Review, please register an account", "information")

    elif session["userID"] and request.method == 'GET':
        print(session["userID"])
        user_data = Single_User_Query(userID=session["userID"])
        print(user_data)
        form.username.data = user_data.get("username")
        form.xboxname.data = user_data.get("xboxname") or None
        form.arenarank.data = user_data.get("arenarank") or None
        return render_template('ytrequests.html', form=form)
    
    elif request.method == 'POST':
        form.validate_on_submit()
        action = register_new_YT_request(form, session["userID"])
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
    """ allows users to submit coaching requests, backfills form if user is logged in with their profile data"""
    form = CoachingForm()
    user_data = {"" : ""}
    
    if request.method == 'POST':
        if form.validate_on_submit():
            coachingRequest = register_new_coaching_request(form)
            if coachingRequest:
                flash("thank you for submitting your request, it is now on your profile where you can see it's progress", "success")
                return redirect(url_for('content.index'))
            else:
                flash("there was an issue with your submission, please try again. If this persists, contact an admin", "warning")
                return redirect(url_for('content.coaching'))

    else:
        #backfill user data if they're logged in UX :)
        if session.get('userID'):
            user_data = Single_User_Query("self", session.get('userID'))
            form.timezone.data = user_data["timezone"]
            form.username.data = user_data["username"]
            form.email.data = user_data["email"]
            form.xboxname.data = user_data["xboxname"]
            form.arenarank.data = user_data["arenarank"]

        return render_template('coaching.html', form=form, user_data=user_data)

@content.route('/map_page', methods=['GET'])
def maps_all():
    """ returns a webpage that lists all maps in HaloData.py"""
    return render_template('allmaps.html', HALO_3_DATA=HALO_3_DATA, GAME_MODES=GAME_MODES)

@content.route('/map_page/<mapID>', methods=['GET'])
def map_page(mapID):
    """ returns video and game data about select map"""
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
