#external modules
from flask import render_template, redirect, url_for, flash, request
import os

#python modules
from functools import wraps

#app imports
from app.data.db import create_database, db_path
from app.services import *
from app.forms import ArticleForm
from app.data.routes import Data_Send_Article_IMG

#db functions
from app.data.db_services_articles import All_Articles_Query, Single_Article_Query, Register_New_Article, Get_Article_Data, Modify_Article_Data, Delete_Article, Toggle_Article_Visibility, Test_Article
from app.data.db_services_videos import All_Videos_Query, Single_Video_Query, Toggle_Video_Visibility

#self module
from . import admin
from .services import Post_Form_Match_Case
from .services_video import Update_Video_Database_Full, Google_API_V3_Write_Thumbnails
from .services_users import All_Users_Management_Query, Delete_User, Ban_User, Unban_User, Update_User_Tags, Update_User_Is_Admin

   

##################
#-----Routes-----#
##################


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
                return redirect(url_for("admin.video_management")) #TODO

            case "article":
                return redirect(url_for("admin.article_management")) #TODO

            case "user":
                return redirect(url_for("admin.user_management")) #TODO
            
            case "database":
                return redirect(url_for("admin.database_management"))
            
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

#TODO: ADAM 17th DECEMBER 2025
@admin.route('/database-management', methods=[ "GET", "POST"])
def database_management():
    pass


#TODO: admin user management
@admin.route('/user-management', methods=["GET", "POST"])
def user_management():
    

    if request.method == "GET":
        users = All_Users_Management_Query()
        return render_template('management-user.html', users=users)

    elif request.method == "POST":

        matchCase = Post_Form_Match_Case(request.form.get("userAction"))
        action = matchCase[0]
        userID = matchCase[1]

        match action:

            case "user_new":
                pass
            case "user_delete":
                flag = Delete_User(userID)
            case "user_ban":
                flag = Ban_User(userID)
            case "user_unban":
                flag = Unban_User(userID)
            case "user_tags":
                new_tags = request.form.get("newTags")  # from input field
                flag = Update_User_Tags(userID, new_tags)
            case _:
                flag = False
                flash("Unknown user action", "danger")
                return redirect(url_for("admin.user_management"))
            
        if flag:
            flash(f"successfully carried out action ({action}) on user ({userID})")
        elif not flag:
            flash(f"could not carry out action ({action}) on user ({userID})")

    else:
        flash("Internal routing error", "danger")
        return redirect(url_for("admin.user_management"))