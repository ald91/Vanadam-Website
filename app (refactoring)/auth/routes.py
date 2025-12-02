#external modules
from flask import Blueprint, render_template, redirect, url_for, request

#python modules
from functools import wraps

#self module
from . import auth

#app imports


##################
#-----Routes-----#
##################

#Admin dashboard
@auth.route('/', methods=["GET", "POST"])
def dashboard():
    """ authentication handling """
    return render_template("")


