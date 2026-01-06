#external modules
from flask import render_template, redirect, url_for, flash, request, session

#app imports
from app.forms import ArticleForm, AdminUserForm, CoachingForm, YouTubeReviewForm
from app.services import post_form_match_case

#db functions
from app.data.db_services_articles import all_articles_query, single_article_query, register_new_article, get_article_data, modify_article_data, delete_article, toggle_article_visibility, test_article
from app.data.db_services_videos import All_Videos_Query, Toggle_Video_Visibility
from app.data.db_services_users import Single_User_Query, Modify_User_Data
from app.data.db_services_coaching import coaching_query, coaching_record_modify, coaching_record_modify_quick, coaching_form_data_prep, youtube_query, YT_record_modify_quick, youtube_record_modify

#self module
from . import admin

from .services_video import Update_Video_Database_Full, Google_API_V3_Write_Thumbnails
from .services_users import All_Users_Management_Query, Delete_User, Ban_User, Unban_User
##################
#-----Routes-----#
##################
@admin.before_request
def require_admin():
    """ ensures anyone accessing dashboard is flag isAdmin=True before allowing access"""
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
            case "coaching":
                return redirect(url_for("admin.coaching_management"))
            case "youtube":
                return redirect(url_for("admin.youtube_management"))
            case "quickvid":
                Update_Video_Database_Full()
                flash("Video Database Update Completed", "success")
                return redirect(url_for("admin.dashboard"))
            case _:
                pass
    else:    
        return redirect(url_for("admin.dashboard"))
    
    return redirect(url_for("admin.dashboard"))

@admin.route('/video-management', methods=["GET", "POST"])
def video_management():
    """ video table related admin actions"""

    if request.method == "GET":
        videos = All_Videos_Query(True)
        return render_template('management-video.html', videos=videos)
        
    elif request.method == "POST":
        
        match_case = post_form_match_case(request.form.get("videoAction"))
        action = match_case[0] 
        vidID = match_case[1]
    
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
                return redirect(url_for("admin.video_management"))
    else:
        flash("internal routing error", "danger")
        return redirect(url_for("admin.video_management"))

@admin.route('/article-management', methods=["GET", "POST"])
def article_management():
    """ article documents and table related admin actions"""
    
    articles: list[dict] = all_articles_query(True)

    if request.method == "GET":
        return render_template('management-article.html', articles=articles)  
          
    elif request.method == "POST":
        
        #JINJA 2 sends "articleAction(Article.ID)"
        match_case = post_form_match_case(request.form.get("articleAction"))
        action = match_case[0]
        articleID = match_case[1]

        match action:
            case "article_new":
                return redirect(url_for("admin.article_management_new"))

            case "article_modify":
                return redirect(url_for("admin.article_management_individual", articleID=articleID))
            
            case "article_delete":
                flag = delete_article(articleID)
                if flag == False:
                    flash("unable to delete article, an error has occured", "danger")
                    return redirect(url_for("admin.article_management"))

                else:
                    flash(f"article {articleID} has been Deleted successfully", "success")
                    return redirect(url_for("admin.article_management"))           
            case "article_toggle":
                flag = toggle_article_visibility(articleID)
                if flag == False:
                    flash("Unable to toggle article visiblilty", "danger")
                flash("successfull changed article visiblity", "success")
                return render_template('management-article.html', articles=articles)   

            case "test_article":
                flag = test_article() 
                if not flag:
                    flash("untable to initiate test article, did u try this on a populated DB?", "danger")
                flash("test article initiated")
                return redirect(url_for("admin.article_management"))  
    else:
        flash("internal routing error", "danger")
        return redirect(url_for("admin.article_management"))   
    flash("internal routing error", "danger")
    return redirect(url_for("admin.article_management"))

@admin.route('/article-management/new', methods=['GET', 'POST'])
def article_management_new():
    """ creation of a new article using form object """
    form = ArticleForm()
    if request.method == "POST":
        if form.validate_on_submit():
            print("form validated on submit")
            register_new_article(form)
            print("Article Created")
            flash("New article created")
            return redirect(url_for("admin.article_management"))
    
    return render_template('management-article-new.html', form=form)

@admin.route('/article-management/<int:articleID>', methods=["GET", "POST"])
def article_management_individual(articleID):
    """ retrieves and allows editing of a sigle article file by ID"""
    form = ArticleForm()

    if request.method == "GET":
        article_data = single_article_query(articleID)
        article_text = get_article_data(articleID)

        form.title.data = article_text["articleTitle"] #json
        form.description.data = article_text["articleDescription"] #json
        form.content.data = article_text["article_content"] #json
        form.tags.data = article_text["articleTags"] #json
        form.hidden.data = article_data["hidden"] #db

        return render_template('management-article-individual.html', article_data=article_data, form=form, article_text=article_text )

    if request.method == "POST":
        if form.validate_on_submit():
            modify_attempt = modify_article_data(articleID, form)
            if modify_attempt:
                flash("Article updated successfully", "success")
                return redirect(url_for('admin.article_management'))

            else:
                flash("Article update failed", "danger")
                return redirect(url_for('admin.article_management'))
        else:
            flash("form entry error", "danger")
            return render_template("management-article.html", articleID=articleID) #sends user back to edit if there is an error

@admin.route('/user-management', methods=["GET", "POST"])
def user_management():
    """ admin dashboard for user accounts"""
    all_user_data = All_Users_Management_Query()
    print(all_user_data)

    if request.method == "GET":
        return render_template('management-user.html', all_user_data=all_user_data)

    elif request.method == "POST":

        match_case = post_form_match_case(request.form.get("userAction"))
        print(match_case)
        action = match_case[0]
        userID = match_case[1]

        match action:

            case "user_new":
                pass
            case "user_modify":
                return redirect(url_for('admin.user_management_individual', userID=userID))
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

@admin.route('/user-management/<int:userID>', methods=["GET", "POST"])
def user_management_individual(userID: str):
    """ search and retrieve a user's data based on user ID, gives an editable form object"""
    form = AdminUserForm()
    
    if request.method == "GET":
        user_data = Single_User_Query("admin", userID)
        form.username.data = user_data["username"] 
        form.email.data = user_data["email"]
        form.xboxname.data = user_data["xboxname"]
        form.timezone.data = user_data["timezone"]
        form.arenarank.data = user_data["arenarank"]
        form.isAdmin.data = user_data["isAdmin"] | False
        form.banned.data = user_data["banned"]  | False
        return render_template('management-user-individual.html', form=form, user_data=user_data)  
    elif request.method =="POST":
        flag = None
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
    """ shows all coaching requests from the database CoachingRequests table"""
    all_crequests_data = coaching_query("admin")

    if request.method == "GET":
        return render_template('management-coaching.html', all_crequests_data=all_crequests_data)
    elif request.method == "POST":
        match_case = post_form_match_case(request.form.get("coachingAction"))
        action = match_case[0] 
        crequestID = int(match_case[1])

        print(action, crequestID)

        match action:
            case "modify":
                return redirect(url_for('admin.coaching_management_request', crequestID=crequestID))
            case "delivered":
                if coaching_record_modify_quick(crequestID, action):
                    flash(f"successfully marked ({crequestID}) as {action}","success")
            case "paid":
                if coaching_record_modify_quick(crequestID, action):
                    flash(f"successfully marked ({crequestID}) as {action}","success")
            case "delete":
                if coaching_record_modify_quick(crequestID, action):
                    flash(f"successfully marked ({crequestID}) as {action}","success")
            case _:
                flash("invalid request","warning")

    return redirect(url_for('admin.coaching_management'))

@admin.route('/coaching-requests/<int:crequestID>', methods=["GET", "POST"])
def coaching_management_request(crequestID):
    """ retrieve the select coaching request (crequest) information from the database and provide a form that can be modified"""
    if request.method == "GET":
        crequestData = coaching_query("admin", crequestID=crequestID)
        crequestData = crequestData[0]
        form = coaching_form_data_prep(crequestData) 
        return render_template('management-coaching-individual.html', crequestData=crequestData, form=form)
    elif request.method == "POST":
        form = CoachingForm()
        flag = coaching_record_modify(crequestID, form)
        if not flag:
            flash(f"unable to update record {crequestID} an error occurded", "warning")
            return redirect(url_for('admin.coaching_management_request', crequestID=crequestID))
        else:
            flash(f"updated record {crequestID} successfully", "success")
            return redirect(url_for('admin.coaching_management'))
    flash("unexpected outcome", "critical")
    return redirect(url_for('admin.coaching_management'))

@admin.route('/youtube-requests', methods=["GET", "POST"])
def youtube_management():
    """ show all YouTube VoD review requests from the database"""
    all_YT_request_data = youtube_query("admin")

    if request.method == "GET":
        return render_template('management-youtube.html', all_YT_request_data=all_YT_request_data)  
    
    
    elif request.method == "POST":
        match_case = post_form_match_case(request.form.get("youtubeAction"))
        action = match_case[0] 
        YTrequestID = int(match_case[1])

        print(action, YTrequestID)

        match action:
            case "modify":
                return redirect(url_for('admin.youtube_management_request', YTrequestID=YTrequestID))
            case "uploaded":
                if YT_record_modify_quick(YTrequestID, action):
                    flash(f"successfully marked ({YTrequestID}) as {action}","success")
            case "recorded":
                if YT_record_modify_quick(YTrequestID, action):
                    flash(f"successfully marked ({YTrequestID}) as {action}","success")
            case "queued":
                if YT_record_modify_quick(YTrequestID, action):
                    flash(f"successfully marked ({YTrequestID}) as {action}","success")
            case "delete":
                if YT_record_modify_quick(YTrequestID, action):
                    flash(f"successfully marked ({YTrequestID}) as {action}","success")
            case _:
                flash("invalid request","warning")

    return redirect(url_for('admin.youtube_management'))

@admin.route('/youtube-requests/<int:YTrequestID>', methods=["GET", "POST"])
def youtube_management_request(YTrequestID):
    """ retrieve and modify a single youtube request by ID from the database. provides an editable form"""
    form = YouTubeReviewForm()   
    if request.method == "GET":
        YT_request_data = youtube_query("admin", YTrequestID=YTrequestID)
        YT_request_data = YT_request_data[0]

        form.YTrequestID.data      = YT_request_data["YTrequestID"]
        form.YTrequestTime.data    = YT_request_data["YTrequestTime"]
        form.username.data         = YT_request_data["username"]
        form.xboxname.data         = YT_request_data["xboxname"]
        form.arenarank.data        = YT_request_data["arenarank"]
        form.videoURL.data         = YT_request_data["videoURL"]
        form.trackernetwork.data   = YT_request_data["trackernetwork"]
        form.playlist.data         = YT_request_data["playlist"]
        form.matchmap.data         = YT_request_data["matchmap"]
        form.matchgamemode.data    = YT_request_data["matchgamemode"]
        form.status.data           = YT_request_data["status"]
        form.youtubevideoID.data       = YT_request_data["youtubevideoID"]    
        return render_template('management-youtube-individual.html', YT_request_data=YT_request_data, form=form)

    elif request.method == "POST":
        flag = youtube_record_modify(YTrequestID, form)
        if not flag:
            flash(f"unable to update record {YTrequestID} an error occurded", "warning")
            return redirect(url_for('admin.youtube_management_request', YTrequestID=YTrequestID))
        else:
            flash(f"updated record {YTrequestID} successfully", "success")
            return redirect(url_for('admin.youtube_management'))
    flash("unexpected outcome", "critical")
    return redirect(url_for('admin.youtube_management'))
