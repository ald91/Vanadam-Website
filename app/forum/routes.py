
#external modules
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, abort


#python modules
from functools import wraps

#internal module
from . import forum
from .services import prefill, modify, post, comment, delete_post_record, delete_comment_record, fetch_all, fetch_one, fetch_comments, file_report
from ..forms import ForumForm, CommentForm, ReportForm
from ..services import check_ban
from ..decorators import login_required
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
    username = session['username']

    if form.validate_on_submit() and not check_ban(username):
        post(form, username)
        print("Article Created")
        return redirect(url_for("forum.forum_page"))

    return render_template("create_post.html", form=form, username=username)

@login_required
@forum.route('/<id>/comment', methods=["GET", "POST"])
def create_comment(id):
    form = CommentForm()
    username = session.get('username')

    if form.validate_on_submit() and not check_ban(username):
        comment(form, id, username)
        print("Comment Created")

    return redirect(url_for("forum.view_post", id=id, username=username))

@forum.route('/<id>/view', methods=["GET"])
def view_post(id):
    post = fetch_one(id)
    comments = fetch_comments(id)
    comment_form = CommentForm()
    current_user = session.get('username')
    report_form = ReportForm()

    return render_template("view_post.html", post=post, comment=comment_form, comments=comments, current_user=current_user, report_form=report_form)

@forum.route('/<id>/edit', methods=["GET", "POST"])
def edit_post(id):
    form = ForumForm()

    if not form.validate_on_submit():
        form = prefill(form, id)

    if form.validate_on_submit():
        modify(form, id)

    return render_template("edit_post.html", form=form)

@forum.route('/<id>/delete', methods=["GET", "DELETE"])
def delete_post(id):
    delete_post_record(id)
    return redirect(url_for("forum.forum_page"))

@forum.route('/<id>/report', methods=["GET", "POST"])
@login_required
def report(id):
    form = ReportForm()
    current_user = session.get('username')
    form.target_id.data = id
    if current_user is not None and form.validate_on_submit():
        print("Report Started")
        file_report(form, current_user)
        return redirect("view")
    return render_template("report.html", target_id=id, form=form)

