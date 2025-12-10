
#external modules
from flask import Blueprint, render_template, redirect, url_for, request


#python modules
from functools import wraps

#internal module
from . import forum

##################
#-----Routes-----#
##################

#Admin dashboard
@forum.route('/LFG', methods=["GET", "POST"])
def forum_page():
    """ forum entry point """
    if request.method == "GET":
        return render_template("forum.html")
    
    elif request.method == "POST":
        pass

@forum.route('/LFG/create', methods=["GET", "POST"])
def create_post():
    pass

@forum.route('/LFG/<id>', methods=["GET", "POST"])
def view_post():
    pass