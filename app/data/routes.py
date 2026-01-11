#flask imports
from flask import send_from_directory, current_app
import os

#app imports


#internal 
from . import data


@data.route('/articles_img/<filename>')
def data_send_article_img(filename: str) -> str:
    """ returns a file path for article images x.jpeg. App cannot return files outside of static, this keeps data 
    in data so article files are easier to manage """
    folder_path = os.path.join(current_app.root_path, "data/articles/ArticlesIMG")

    return send_from_directory(folder_path, filename)

#TODO: NYI do after submissions
@data.route('/coaching/<filename>')
def data_send_coaching_JSON(filename: str) -> dict:

    """ NYI looks in coaching dir and returns associated JSON file with fields"""

