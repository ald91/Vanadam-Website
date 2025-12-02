
#external modules
from flask import Blueprint, render_template, redirect, url_for, request


#python modules
from functools import wraps

#set admin route
admin = Blueprint("admin", __name__, template_folder="templates")



##################
#-----Routes-----#
##################

#Admin dashboard
@admin.route('/', methods=["GET", "POST"])
def dashboard():
    """ admin dashboard """
    return render_template("")