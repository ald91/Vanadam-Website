
#external modules
from flask import Blueprint, render_template, redirect, url_for, request, session


#python modules
from functools import wraps

#internal module
from . import forum
from .services import prefill, modify, post
from ..forms import ForumForm, MessageForm
from ..services import checkTags
from ..data.db import get_database

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
def post_create():
    form = ForumForm()

    if form.validate_on_submit():
        post(form)
        print("Article Created")

@forum.route('/LFG/<id>', methods=["GET", "POST"])
def edit_post(id):
    form = ForumForm()

    if not form.validate_on_submit():
        form = prefill(form)

    if form.validate_on_submit():
        modify(form)

    pass

@forum.route('/LFG/<id>', methods=["GET", "DELETE"])
def delete_post(id):
    db = get_database()
    cur = db.cursor()

    #Only permit original poster to delete own post, admin deletion handled elsewhere
    query = "SELECT username FROM Forums WHERE id = ?"
    cur.execute(query, (id,))
    result = dict(cur.fetchone())

    if session["username"] == result["username"]:
        query = "DELETE FROM Forums WHERE id = ?"
        cur.execute(query, (id,))
    return redirect(url_for("forum_page"))

@forum.route('/LFG/<id>', methods=["GET", "POST"])
def create_comment(id):
    form = MessageForm()
    pass

@forum.route('/LFG/<id>', methods=["GET"])
def view_post():
    pass