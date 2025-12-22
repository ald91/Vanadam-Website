#flask imports
from flask import send_from_directory, current_app
import os

#app imports


#internal 
from . import data


@data.route('/articles_img/<filename>')
def Data_Send_Article_IMG(filename: str) -> str:
    
    """ returns a file path for article images x.jpeg. App cannot return files outside of static, this keeps data 
     in data so article files are easier to manage """
    
    folder_path = os.path.join(current_app.root_path, "Data/Articles/ArticlesIMG")

    return send_from_directory(folder_path, filename)

@data.route('/coaching/<filename>')
def Data_Send_Coaching_JSON(filename: str) -> dict:

    """ looks in coaching dir and returns associated JSON file with fields TODO"""

    pass

