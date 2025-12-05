#external modules
from flask import render_template, redirect, url_for, flash, request
import os

#python modules
from functools import wraps

#app imports
from app.data.db import create_database, db_path
from app.services import *

#self module
from . import admin
from .services_video import Update_Video_Database_Full, Full_Video_Management_Query, Google_API_V3_Write_Thumbnails
from .services_article import Full_Article_Management_Query


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
@admin.route('article-management')
def article_management():
    """ article documents and table related admin actions"""
            
    if request.method == "GET":
        articles = Full_Article_Management_Query()
        return render_template('admin/management-article.html', articles=articles)  
          
    elif request.method == "POST":
        
        #JINJA 2 sends "articleAction(Article.ID)"
        input = request.form.get("articleAction").split("(")
        action = input[0]
        articleID = input[1].split(")")
    
        match action:
            case "article_new":
                #TODO - ARTICLE NEW REDIRECTION FOR ADMINS
                return redirect(url_for("admin.article_management"))

            case "article_modify":
                #TODO - ARTICLE MODIFY FUNCTION
                return redirect(url_for(f"admin.article_management", articleID=articleID))
            
            case "article_delete":
                #TODO - ARTICLE DELETE FUNCTION
                return redirect(url_for(f"admin.article_delete", articleID=articleID))
            
            case "article_toggle":
                #TODO - ARTICLE TOGGLE FUNCTION
                return redirect(url_for(f"admin.article_management", articleID=articleID))    
    else:
        flash("internal routing error", "error")
        return redirect(url_for("admin.article_management"))



#TODO: admin user management
@admin.route('user-management')
def user_management():
    """ modify user data """
    pass
