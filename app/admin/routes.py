#external modules
from flask import render_template, redirect, url_for, flash, request
import os

#python modules
from functools import wraps

#app
from ..db import create_database, dbpath
from ..services import *

#self module
from . import admin
from .services import Update_Video_Database_Full


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

        #VIDEO DATABASE ACTIONS
        if request.form.get("dbAction"):
            action = request.form.get("dbAction")
        
            if action == "vdbUpdate":
                Update_Video_Database_Full()
                flash("Video Database Update Completed", "success")
                return redirect(url_for("admin.dashboard"))
            
            elif action == "vdbDelete":
                dbpath = "database.db"
                try:
                    os.remove(dbpath)
                    create_database()
                    flash("Video Database delete attempted", "success")
                    return redirect(url_for("admin.dashboard"))
                    
                except FileNotFoundError:
                    flash("Could not delete database", "error")
                    return redirect(url_for("admin.dashboard"))

    return redirect(url_for("admin.dashboard"))
        
    
    

#TODO: admin videos
@admin.route('/videos-management', methods=["GET", "PATCH"])
def video_management():
    """ video table related admin actions"""
    pass


#TODO: admin articles
@admin.route('article-route')
def article_management():
    """ posts table related admin actions"""
    pass


#TODO: admin user management
@admin.route('user-management')
def user_management():
    """ modify user data """
    pass
