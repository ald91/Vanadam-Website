#external modules
from flask import render_template, redirect, url_for, flash, request
import os

#python modules
from functools import wraps

#app imports
from app.data.db import create_database, db_path
from app.services import *
from app.forms import ArticleForm

#self module
from . import admin
from .services_video import Update_Video_Database_Full, Full_Video_Management_Query, Google_API_V3_Write_Thumbnails
from .services_article import All_Articles_Management_Query, Single_Article_Query, Register_New_Article, Get_Article_Data
from .services_users import All_Users_Management_Query

   

##################
#-----Routes-----#
##################


@admin.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    """ admin dashboard """
    if request.method == "GET":
        return render_template('admin/dashboard.html')

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
            
            case "gamedata":
                return redirect(url_for("admin.gamedata_management")) #TODO
            
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
            
    if request.method == "GET":
        videos = Full_Video_Management_Query()
        return render_template('admin/management-video.html', videos=videos)
        
    elif request.method == "POST":
        
        action = request.form.get("videoAction")
    
        match action:
            case "video_thumbnails":
                flash("Video thumbnails folder update completes", "success")
                Google_API_V3_Write_Thumbnails()
                return redirect(url_for("admin.video_management"))

            case "video_data":
                Update_Video_Database_Full()
                flash("Video database update completed", "success")
                return redirect(url_for("admin.video_management"))
        
    else:
        flash("internal routing error", "error")
        return redirect(url_for("admin.video_management"))

#TODO: admin articles
@admin.route('/article-management', methods=["GET", "POST"])
def article_management():
    """ article documents and table related admin actions"""
            
    if request.method == "GET":
        articles = All_Articles_Management_Query()
        return render_template('admin/management-article.html', articles=articles)  
          
    elif request.method == "POST":
        
        #JINJA 2 sends "articleAction(Article.ID)"
        check = "("
        input = request.form.get("articleAction")

        if check in input:
            input = request.form.get("articleAction").split("(")
            action = str(input[0])
            articleID = input[1].replace("(","").replace(")","")
        else:
            action = str(input)
    
        print(action)

        match action:
            case "article_new":
                return redirect(url_for("admin.article_management_new"))

            case "article_modify":
                #TODO - ARTICLE MODIFY FUNCTION
                return redirect(url_for(f"admin.article_management_individual", articleID=articleID))
            
            case "article_delete":
                #TODO - ARTICLE DELETE FUNCTION
                return redirect(url_for(f"admin.article_delete", articleID=articleID))
            
            case "article_toggle":
                #TODO - ARTICLE TOGGLE FUNCTION
                return redirect(url_for(f"admin.article_management", articleID=articleID))    
    else:
        flash("internal routing error", "error")
        return redirect(url_for("admin.article_management"))
    
    flash("internal routing error", "error")
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
    
    return render_template('admin/management-article-new.html', form=form)

#TODO
@admin.route('/article-management/<articleID>', methods=["GET", "POST"])
def article_management_individual(articleID):
    
    if request.method == "GET":
        articleData = Single_Article_Query(articleID)
        articleText = Get_Article_Data(articleID)
        form = ArticleForm()
        print(articleData)
        return render_template('admin/management-article-individual.html', articleData=articleData, form=form, articleText=articleText )


#TODO: admin user management
# TODO: admin user management
@admin.route('/user-management', methods=["GET", "POST"])
def user_management():
    """ modify user data """

    if request.method == "GET":
        # TODO: Replace with your real query
        users = All_Users_Management_Query()
        return render_template('admin/management-user.html', users=users)

    elif request.method == "POST":

        # Jinja sends: userAction(userID)
        raw_input = request.form.get("userAction")

        check = "("
        if check in raw_input:
            split_input = raw_input.split("(")
            action = split_input[0]
            userID = split_input[1].replace(")", "")
        else:
            action = raw_input
            userID = None

        print("Action:", action)
        print("UserID:", userID)

        match action:

            #CREATE USER (Redirect to form)
            case "user_new":
                return redirect(url_for("admin.user_management_new"))

            #DELETE USER
            case "user_delete":
                Delete_User(userID)
                flash("User deleted successfully", "success")
                return redirect(url_for("admin.user_management"))

            #BAN USER
            case "user_ban":
                Ban_User(userID)
                flash("User banned successfully", "success")
                return redirect(url_for("admin.user_management"))

            #UNBAN USER
            case "user_unban":
                Unban_User(userID)
                flash("User unbanned successfully", "success")
                return redirect(url_for("admin.user_management"))

            #CHANGE USER TAGS
            case "user_tags":
                new_tags = request.form.get("newTags")  # from input field
                Update_User_Tags(userID, new_tags)
                flash("User tags updated", "success")
                return redirect(url_for("admin.user_management"))

            case _:
                flash("Unknown user action", "error")
                return redirect(url_for("admin.user_management"))

    else:
        flash("Internal routing error", "error")
        return redirect(url_for("admin.user_management"))

