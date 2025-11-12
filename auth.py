#Flask
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, g
from flask_mail import Mail

#Databases
import sqlite3, os, hashlib, base64
from dbconstructor import create_database


#Security
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

#internal imports
#=================
from extensions import app
from db import get_database
from auth import *
from dbconstructor import *
from HaloData import *
from formclasses import LoginForm, RegisterForm, SearchForm, RecoveryForm

#password recovery serializer
serializer = URLSafeTimedSerializer(app.secret_key)

#email functionality 
mail = Mail(app)

def log_in_user(form):
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data 
       
        db = get_database()
        cur = db.cursor()

        query = "SELECT * FROM Users WHERE username = ?"
        cur.execute(query, (username,))
        result = cur.fetchone()

        form = LoginForm()

        if result is None:
            print("User not found")
            flash("Incorrect username or password.", "error")
            return render_template('login.html', form=form)
        hashed_input = hashlib.sha256(password.encode()).hexdigest()
        stored_password = result['password']



        if hashed_input == stored_password:
            #Clear session data to remove stale data, then fill in session data
            session.clear()
            session['username'] = result['username']
            return True
        
        else:
            return False


def register_user(form):
        if form.validate_on_submit():  # If form passes validation rules
            username = form.username.data
            email = form.email.data
            password = form.password.data
            password2 = form.password2.data
            print("RegisterForm has been validated")

            if password != password2:
                flash("Passwords don't match!", "error")
                return render_template('register.html', form=form)

            db = get_database()
            cur = db.cursor()

            query = "SELECT * FROM Users WHERE username = ? OR email = ?"
            cur.execute(query, (username, email))
            existing_user = cur.fetchone()

            if existing_user is None:
                # Hash password and insert new user record
                hashpass = hashlib.sha256(password.encode()).hexdigest()
                cur.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
                            (username, email, hashpass))
                db.commit()
                session['username'] = username
                

                return session['username']
            else:
                return False

        return redirect(url_for('register'))

#Pass reset email token
def verify_reset_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt= app.security_password_salt , max_age=expiration)
    except Exception:
        return None
    return email

def send_recovery_email(email, username):
    token = serializer
    reset_url = url_for('reset-password', token=token, _external=True)

    msg = Message(
        subject="Vanadam Halo - Password Reset Request",
        sender="VanadamEsports@gmail.com",
        recipients= email,
    )
    msg.body = render_template("email/password_reset.txt", username=username, reset_url=reset_url)
    mail.send(msg)

def recover_user(form):
    username = form.username.data
    email = form.email.data
        
    print(f"A recovery attempt for account: {username} and email: {email} was attempted.")
            
    db = get_database()
    cur = db.cursor()

    query = 'SELECT * FROM Users WHERE username = ? COLLATE NOCASE AND email = ? COLLATE NOCASE'
    cur.execute(query, (username, email))
    existing_user = cur.fetchone()

    if existing_user:
        x = "1234"
        send_recovery_email(email, username)
        flash(f"Recovery Email Sent, Valid for {x} Hours", "success")

        
        return redirect(url_for('index'))
    else:
        flash("Details incorrect", "error")
        return redirect(url_for('recovery'))


