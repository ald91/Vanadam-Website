
#external modules
from flask import Blueprint, render_template, redirect, url_for, request


#python modules
from functools import wraps

#internal module
from . import forum
from .services import prefill, modify, post, comment, delete, fetch_all, fetch_one, fetch_comments
from ..forms import ForumForm, CommentForm
from ..services import login_required
from ..data.db import get_database

##################
#-----Routes-----#
##################

#Admin dashboard
@forum.route('/', methods=["GET", "POST"])
def forum_page():
    """ forum entry point """
    if request.method == "GET":
        posts = fetch_all()
    
    elif request.method == "POST":
        pass

    return render_template("all_forums.html", posts=posts)

@forum.route('/create', methods=["GET", "POST"])
@login_required
def create_post():
    form = ForumForm()

    if form.validate_on_submit():
        post(form)
        print("Article Created")
        return redirect(url_for("forum_page"))

    return render_template("create_post.html", form=form)

@login_required
@forum.route('/<id>/comment', methods=["GET", "POST"])
def create_comment(id):
    form = CommentForm()

    if form.validate_on_submit():
        comment(form, id)
        print("Comment Created")

    return redirect(url_for("forum.view_post", id=id))

@forum.route('/<id>/view', methods=["GET"])
def view_post(id):
    post = fetch_one(id)
    comments = fetch_comments(id)
    comment_form = CommentForm()

    return render_template("view_post.html", post=post, comment=comment_form,comments=comments)

#TODO: Create edit template
@forum.route('/<id>/edit', methods=["GET", "POST"])
def edit_post(id):
    form = ForumForm()

    if not form.validate_on_submit():
        form = prefill(form)

    if form.validate_on_submit():
        modify(form)

    pass

@forum.route('/<id>/delete', methods=["GET", "DELETE"])
def delete_post(post_id):
    delete(post_id)
    return redirect(url_for("forum_page"))
