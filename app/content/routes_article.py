

#external modules
from flask import Blueprint, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

# app imports
from app.data.db import get_database
from app.forms import ArticleForm
from app.classes import Article
from app.services import checkTags

#data imports
from app.data.db_services_articles import all_articles_query, single_article_query, article_JSON_load

#self import
from . import content

@content.route('/articles', methods=["GET"])
def article():
    articles = all_articles_query()
    return render_template('allarticles.html', articles=articles)

@content.route('/articles/<articleID>', methods=['GET'])
def article_view(articleID):
    article = single_article_query(articleID)
    content = article_JSON_load(articleID)
    return render_template("article_view.html", article=article, content=content)
