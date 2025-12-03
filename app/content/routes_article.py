

#external modules
from flask import Blueprint, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

# app imports
from ..db import get_database
from ..forms import ArticleForm
from ..services import checkTags

#internal import
from . import content

#TODO: article upload folder
uploadFolder = None

@content.route('/articles')
def article():
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM articles"
    cur.execute(query)

    article_results = cur.fetchall()
    article_results = [dict(row) for row in article_results]

    print(article_results)

    return redirect(url_for('article_create'))
    #return render_template('article_view.html')

@content.route('/articles/<id>', methods=['GET', 'PATCH', 'POST', 'DELETE'])
def article_view(id):
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM articles WHERE articleID = ?"
    cur.execute(query, (id,))
    row = cur.fetchone()

    if row is None:
        flash("Article does not exist", "error")
        return render_template('siteerror.html')

    article = dict(row)

    return render_template("content/article_view.html", article=article)

@content.route('/articles/create', methods=['GET', 'POST'])
def article_create():
    form = ArticleForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        tags = form.tags.data

        checkTags("Article", tags)

        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            image_path = os.path.join(uploadFolder, filename)
            file.save(image_path)

        db = get_database()
        cur = db.cursor()

        query = "INSERT INTO Articles (title, content, tags, image_filename) VALUES (?, ?, ?, ?)"
        cur.execute(query, (title, content, filename))
        db.commit()

        print("Article Created")
    return render_template('content/articles/article_create.html', form=form)

@content.route('/articles/<id>/edit', methods=['GET', 'PATCH', 'POST', 'DELETE'])
def article_edit(id):
    db = get_database()
    cur = db.cursor()

    query = "SELECT * FROM articles WHERE articleID = ?"
    cur.execute(query, (id,))
    article = cur.fetchone()
    form = ArticleForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        tags = form.tags.data

        db = get_database()
        cur = db.cursor()

        query = "UPDATE Articles SET title = ?, content = ?, tags = ? WHERE articleID = ?"
        cur.execute(query, (title, content, tags, id))
        db.commit()
        print("Article Edited")
        return redirect(url_for('article_view', id=id))

    return render_template('article_edit.html', id=id, form=form, article=article)
