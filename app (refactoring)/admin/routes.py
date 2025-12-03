#external modules
from flask import render_template, redirect, url_for, flash, request

#python modules
from functools import wraps

#app
from db import create_database

#self module
from . import admin
from .services import *


##################
#-----Routes-----#
##################

#TODO: admin dash
@admin.route('/dashboard', methods=["GET"])
def dashboard():
    """ admin dashboard """
    if request.method == "GET":
        return render_template('admin/dashboard.html')

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
