from flask import session, redirect, url_for, flash
from functools import wraps
from app.data.db import get_database


def login_required(f):

    """ checks using flask dession is a user is in session using their userID """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "userID" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper

