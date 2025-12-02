
#external modules
from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_session import Session

#python modules
from functools import wraps

#set admin route
site = Blueprint("site", __name__, template_folder="templates")



##################
#-----Routes-----#
##################

#Admin dashboard
@site.route('/', methods=["GET"])
def index():
    """ Home Page """

    from services import fetchNewsBar, fetchSideBar    
    fetchSideBar(4) #set number to be retrieved
    fetchNewsBar(8) #set number to be retrieved

    return render_template("")