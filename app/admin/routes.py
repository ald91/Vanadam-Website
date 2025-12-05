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


##################
#-----Routes-----#
##################

#TODO: admin dash
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
        
    
    

#TODO: admin videos (adam)
@admin.route('/video-management', methods=["GET", "POST"])
def video_management():
    """ video table related admin actions"""
            
    if request.method == "GET":
        videos = Full_Video_Management_Query()
        return render_template('admin/video-management.html', videos=videos)
        
    elif request.method == "POST":
        
        action = request.form.get("videoAction")
    
        match action:
            case "video_thumbnails":
                #TODO
                flash("Video thumbnails folder update completes", "success")
                Google_API_V3_Write_Thumbnails()
                return redirect(url_for("admin.video_management"))

            case "video_data":
                Update_Video_Database_Full()
                flash("Video database update completed", "success")
                return redirect(url_for("admin.video_management"))
        
            case "video_modify":
                return
                #TODO
    else:
        flash("internal routing error", "error")
        return redirect(url_for("admin.video_management"))



#TODO: admin articles
@admin.route('article-management')
def article_management():
    """ posts table related admin actions"""
    pass


#TODO: admin user management
@admin.route('user-management')
def user_management():
    """ modify user data """
    pass
