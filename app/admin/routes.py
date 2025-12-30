#external modules
from flask import render_template, redirect, url_for, flash, request
import os

#python modules
from functools import wraps

#app imports
from app.data.db import create_database, db_path
from app.services import *
from app.forms import ArticleForm, AdminUserForm, CoachingForm, YouTubeReviewForm
from app.data.routes import Data_Send_Article_IMG
from app.services import Post_Form_Match_Case

#db functions
from app.data.db_services_articles import All_Articles_Query, Single_Article_Query, Register_New_Article, Get_Article_Data, Modify_Article_Data, Delete_Article, Toggle_Article_Visibility, Test_Article
from app.data.db_services_videos import All_Videos_Query, Single_Video_Query, Toggle_Video_Visibility
from app.data.db_services_users import Single_User_Query, Modify_User_Data
from app.data.db_services_coaching import Coaching_Query, Coaching_Save_JSON, Coaching_Load_JSON, Coaching_Record_Modify, Coaching_Record_Modify_Quick, Coaching_Form_Data_Prep, Youtube_Query, YT_Record_Modify_Quick, youtube_record_modify

#self module
from . import admin

from .services_video import Update_Video_Database_Full, Google_API_V3_Write_Thumbnails
from .services_users import All_Users_Management_Query, Delete_User, Ban_User, Unban_User, Update_User_Tags, Update_User_Is_Admin

   

##################
#-----Routes-----#
##################
@admin.before_request
def require_admin():
    if not session.get('isAdmin'):
        flash("You cannot access this page", "critical")
        return redirect(url_for("content.index"))

@admin.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    """ admin dashboard """
    if request.method == "GET":
        return render_template('dashboard.html')

    elif request.method == "POST":
        
        action = request.form.get("dashboardAction") #dashboard form
        print(action)

        match action:
            case "video":
                return redirect(url_for("admin.video_management"))

            case "article":
                return redirect(url_for("admin.article_management"))

            case "user":
                return redirect(url_for("admin.user_management"))
            
            case "database":
                return redirect(url_for("admin.database_management"))

            case "coaching":
                return redirect(url_for("admin.coaching_management"))
            
            case "youtube":
                return redirect(url_for("admin.youtube_management"))
            
            case "quickvid":
                Update_Video_Database_Full()
                flash("Video Database Update Completed", "success")
                return redirect(url_for("admin.dashboard"))

    
    else:    
        return redirect(url_for("admin.dashboard"))
    
    return redirect(url_for("admin.dashboard"))

@admin.route('/video-management', methods=["GET", "POST"])
def video_management():
    """ video table related admin actions"""
    print(request)

    if request.method == "GET":
        videos = All_Videos_Query(True)
        return render_template('management-video.html', videos=videos)
        
    elif request.method == "POST":
        
        matchCase = Post_Form_Match_Case(request.form.get("videoAction"))
        action = matchCase[0] 
        vidID = matchCase[1]
    
        match action:
            case "video_thumbnails":
                flash("Video thumbnails folder update completes", "success")
                Google_API_V3_Write_Thumbnails()
                return redirect(url_for("admin.video_management"))

            case "video_data":
                Update_Video_Database_Full()
                flash("Video database update completed", "success")
                return redirect(url_for("admin.video_management"))

            case "video_toggle":
                flag = Toggle_Video_Visibility(vidID)
                if not flag:
                    flash(f"could not toggle video {vidID} visibility", "critical")
                else:
                    flash(f"video {vidID} has had it's visibility toggled", "success")
                return redirect(url_for(f"admin.video_management"))
    else:
        flash("internal routing error", "danger")
        return redirect(url_for("admin.video_management"))

@admin.route('/article-management', methods=["GET", "POST"])
def article_management():
    """ article documents and table related admin actions"""
    
    articles: list[dict] = All_Articles_Query(True)

    if request.method == "GET":
        return render_template('management-article.html', articles=articles)  
          
    elif request.method == "POST":
        
        #JINJA 2 sends "articleAction(Article.ID)"
        matchCase = Post_Form_Match_Case(request.form.get("articleAction"))
        action = matchCase[0]
        articleID = matchCase[1]

        match action:
            case "article_new":
                return redirect(url_for("admin.article_management_new"))

            case "article_modify":
                return redirect(url_for(f"admin.article_management_individual", articleID=articleID))
            
            case "article_delete":
                flag = Delete_Article(articleID)
                if flag == False:
                    flash("unable to delete article, an error has occured", "danger")
                    return redirect(url_for("admin.article_management"))

                else:
                    flash(f"article {articleID} has been Deleted successfully", "success")
                    return redirect(url_for("admin.article_management"))
            
            case "article_toggle":
                flag = Toggle_Article_Visibility(articleID)
                if flag == False:
                    flash("Unable to toggle article visiblilty", "danger")
                flash("successfull changed article visiblity", "success")
                return render_template('management-article.html', articles=articles)   

            case "test_article":
                flag = Test_Article() 
                if not flag:
                    flash("untable to initiate test article, did u try this on a populated DB?", "danger")
                flash("test article initiated")
                return redirect(url_for(f"admin.article_management"))  
    else:
        flash("internal routing error", "danger")
        return redirect(url_for("admin.article_management"))
    
    flash("internal routing error", "danger")
    return redirect(url_for("admin.article_management"))

@admin.route('/article-management/new', methods=['GET', 'POST'])
def article_management_new():
    
    form = ArticleForm()
  
    if request.method == "POST":
        print("form is a post request")

        if form.validate_on_submit():
            print("form validated on submit")
            Register_New_Article(form)
            print("Article Created")
            flash("New article created")
            return redirect(url_for("admin.article_management"))
    
    return render_template('management-article-new.html', form=form)

@admin.route('/article-management/<articleID>', methods=["GET", "POST"])
def article_management_individual(articleID):
    
    form = ArticleForm()

    if request.method == "GET":
        articleData = Single_Article_Query(articleID)
        articleText = Get_Article_Data(articleID)

        form.title.data = articleText["articleTitle"] #json
        form.description.data = articleText["articleDescription"] #json
        form.content.data = articleText["articleContent"] #json
        form.tags.data = articleText["articleTags"] #json
        form.hidden.data = articleData["hidden"] #db

        return render_template('management-article-individual.html', articleData=articleData, form=form, articleText=articleText )

    if request.method == "POST":
        if form.validate_on_submit():
            modifyAttempt = Modify_Article_Data(articleID, form)
            if modifyAttempt:
                flash("Article updated successfully", "success")
                return redirect(url_for('admin.article_management'))

            else:
                flash("Article update failed", "danger")
                return redirect(url_for('admin.article_management'))
        else:
            flash("form entry error", "danger")
            return render_template(f"management-article.html", articleID=articleID) #sends user back to edit if there is an error

@admin.route('/user-management', methods=["GET", "POST"])
def user_management():
    
    AllUserData = All_Users_Management_Query()
    print(AllUserData)

    if request.method == "GET":
        return render_template('management-user.html', AllUserData=AllUserData)

    elif request.method == "POST":

        matchCase = Post_Form_Match_Case(request.form.get("userAction"))
        print(matchCase)
        action = matchCase[0]
        userID = matchCase[1]

        match action:

            case "user_new":
                pass
            case "user_modify":
                return redirect(url_for('admin.User_Management_Individual', userID=userID))
            case "user_delete":
                flag = Delete_User(userID)
            case "user_ban":
                flag = Ban_User(userID)
            case "user_unban":
                flag = Unban_User(userID)
            case _:
                flag = False
                flash("Unknown user action", "danger")
            
        if flag:
            flash(f"successfully carried out action ({action}) on user ({userID})", "success")
        elif not flag:
            flash(f"could not carry out action ({action}) on user ({userID})", "critical")

    else:
        flash("Internal routing error", "danger")
    
    return redirect(url_for("admin.user_management"))

@admin.route('/user-management/<userID>', methods=["GET", "POST"])
def User_Management_Individual(userID: str):
    form = AdminUserForm()
    
    if request.method == "GET":
        userData = Single_User_Query("admin", userID)
        form.username.data = userData["username"] 
        form.email.data = userData["email"]
        form.xboxname.data = userData["xboxname"]
        form.timezone.data = userData["timezone"]
        form.arenarank.data = userData["arenarank"]
        form.isAdmin.data = userData["isAdmin"] | False
        form.banned.data = userData["banned"]  | False
        return render_template('management-user-individual.html', form=form, userData=userData)  
    
    elif request.method =="POST":
        if form.validate_on_submit():
                print(f"recieved update request to modify {userID}")
                flag = Modify_User_Data(userID, form)
        if flag:
            flash(f"user data for {userID} has been updated", "success")
        else:
            flash(f"user data for {userID} has not been updated, an error occured", "warning")
        
        return redirect(url_for('admin.user_management'))     
        
    else:
        flash("invalid request parameter", "critical")
        return redirect(url_for('admin.user_management'))
    
@admin.route('/coaching-requests', methods=["GET", "POST"])
def coaching_management():
    
    AllCrequestsData = Coaching_Query("admin")

    if request.method == "GET":
        return render_template('management-coaching.html', AllCrequestsData=AllCrequestsData)  
    
    
    elif request.method == "POST":
        matchCase = Post_Form_Match_Case(request.form.get("coachingAction"))
        action = matchCase[0] 
        crequestID = int(matchCase[1])

        print(action, crequestID)

        match action:
            case "modify":
                return redirect(url_for('admin.coaching_management_request', crequestID=crequestID))
            case "delivered":
                if Coaching_Record_Modify_Quick(crequestID, action):
                    flash(f"successfully marked ({crequestID}) as {action}","success")
            case "paid":
                if Coaching_Record_Modify_Quick(crequestID, action):
                    flash(f"successfully marked ({crequestID}) as {action}","success")
            case "delete":
                if Coaching_Record_Modify_Quick(crequestID, action):
                    flash(f"successfully marked ({crequestID}) as {action}","success")
            case _:
                flash("invalid request","warning")

    return redirect(url_for('admin.coaching_management'))

@admin.route('/coaching-requests/<int:crequestID>', methods=["GET", "POST"])
def coaching_management_request(crequestID):
    if request.method == "GET":
        crequestData = Coaching_Query("admin", crequestID=crequestID)
        crequestData = crequestData[0]
        form = Coaching_Form_Data_Prep(crequestData)
    
        return render_template('management-coaching-individual.html', crequestData=crequestData, form=form)

    elif request.method == "POST":
            form = CoachingForm()
            flag = Coaching_Record_Modify(crequestID, form)
            if not flag:
                flash(f"unable to update record {crequestID} an error occurded", "warning")
                return redirect(url_for('admin.coaching_management_request', crequestID=crequestID))
            else:
                flash(f"updated record {crequestID} successfully", "success")
                return redirect(url_for('admin.coaching_management'))
    flash(f"unexpected outcome", "critical")
    return redirect(url_for('admin.coaching_management'))


@admin.route('/youtube-requests', methods=["GET", "POST"])
def youtube_management():

    AllYTrequestData = Youtube_Query("admin")

    if request.method == "GET":
        return render_template('management-youtube.html', AllYTrequestData=AllYTrequestData)  
    
    
    elif request.method == "POST":
        matchCase = Post_Form_Match_Case(request.form.get("youtubeAction"))
        action = matchCase[0] 
        YTrequestID = int(matchCase[1])

        print(action, YTrequestID)

        match action:
            case "modify":
                return redirect(url_for('admin.youtube_management_request', YTrequestID=YTrequestID))
            case "uploaded":
                if YT_Record_Modify_Quick(YTrequestID, action):
                    flash(f"successfully marked ({YTrequestID}) as {action}","success")
            case "recorded":
                if YT_Record_Modify_Quick(YTrequestID, action):
                    flash(f"successfully marked ({YTrequestID}) as {action}","success")
            case "queued":
                if YT_Record_Modify_Quick(YTrequestID, action):
                    flash(f"successfully marked ({YTrequestID}) as {action}","success")
            case "delete":
                if YT_Record_Modify_Quick(YTrequestID, action):
                    flash(f"successfully marked ({YTrequestID}) as {action}","success")
            case _:
                flash("invalid request","warning")

    return redirect(url_for('admin.youtube_management'))

@admin.route('/youtube-requests/<int:YTrequestID>', methods=["GET", "POST"])
def youtube_management_request(YTrequestID):
    
    form = YouTubeReviewForm()
    
    if request.method == "GET":
        YTrequestData = Youtube_Query("admin", YTrequestID=YTrequestID)
        YTrequestData = YTrequestData[0]

        form.YTrequestID.data      = YTrequestData["YTrequestID"]
        form.YTrequestTime.data    = YTrequestData["YTrequestTime"]
        form.username.data         = YTrequestData["username"]
        form.xboxname.data         = YTrequestData["xboxname"]
        form.arenarank.data        = YTrequestData["arenarank"]
        form.videoURL.data         = YTrequestData["videoURL"]
        form.trackernetwork.data   = YTrequestData["trackernetwork"]
        form.playlist.data         = YTrequestData["playlist"]
        form.matchmap.data         = YTrequestData["matchmap"]
        form.matchgamemode.data    = YTrequestData["matchgamemode"]
        form.status.data           = YTrequestData["status"]
        form.youtubevideoID.data       = YTrequestData["youtubevideoID"]
    
        return render_template('management-coaching-individual.html', YTrequestData=YTrequestData, form=form)

    elif request.method == "POST":
            #TODO ADAM
            flag = youtube_record_modify(YTrequestID, form)
            if not flag:
                flash(f"unable to update record {YTrequestID} an error occurded", "warning")
                return redirect(url_for('admin.youtube_management_request', YTrequestID=YTrequestID))
            else:
                flash(f"updated record {YTrequestID} successfully", "success")
                return redirect(url_for('admin.youtube_management'))
    flash(f"unexpected outcome", "critical")
    return redirect(url_for('admin.youtube_management'))
