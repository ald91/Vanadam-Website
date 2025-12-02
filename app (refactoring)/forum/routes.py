
#external modules
from flask import Blueprint, render_template, redirect, url_for, request


#python modules
from functools import wraps

#set admin route
forum = Blueprint("forum", __name__, template_folder="templates")



##################
#-----Routes-----#
##################

#Admin dashboard
@forum.route('/', methods=["GET"])
def forum():
    """ forum entry point """
    return render_template("")