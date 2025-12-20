#Flask
from flask import render_template, redirect, url_for, flash, session
from flask_mail import Message

#Security
from werkzeug.security import generate_password_hash, check_password_hash

#App Imports
from app.data.db import get_database
from app.extensions import mail, serializer, security_salt

def log_in_user(form):
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data 
       
        db = get_database()
        cur = db.cursor()

        query = "SELECT * FROM Users WHERE username = ?"
        cur.execute(query, (username,))
        result = cur.fetchone()

        if result is None:
            print("User not found")
            flash("Incorrect username or password.", "danger")
            return False
        
        stored_password = result['password']

        if check_password_hash(stored_password, password):
            #Clear session data to remove stale data, then fill in session data
            session.clear()
            session['userID'] = int(result['userID'])
            session['username'] = str(result['username'])
            return True
        
        else:
            return False

def send_registration_email(username,email):
    try:
        msg = Message(
                    subject= f"Account Creation - Welcome to Vanadam Halo, {username}",
                    sender="VanadamEsports@gmail.com",
                    recipients= [email],
                    body = render_template("emails/register.txt", username=username))
        mail.send(msg)
    
        print(f"sent email {msg}")
    
        return True
    
    except:
        return False

def send_recovery_email(email, username):

    token = serializer.dumps(email, salt=security_salt) #salt token generated in app.py
    reset_url = url_for('reset_password', token=token, _external=True)

    msg = Message(
        subject="Vanadam Halo - Password Reset Request",
        sender="VanadamEsports@gmail.com",
        recipients= [email],
        body = render_template("emails/password_reset.txt", username=username, reset_url=reset_url))

    try:
        mail.send(msg)
        print(f'message sent for {username} at {email}')
        return True
    except:
        print('could not send recovery email, internal error')
        return False
    
def register_user(form):
    if form.validate_on_submit():  # If form passes validation rules
        username = form.username.data
        email = form.email.data
        password = form.password.data
        password2 = form.password2.data
        print("RegisterForm has been validated")

        if password != password2:
            flash("Passwords don't match!", "danger")
            return False

        db = get_database()
        cur = db.cursor()

        query = "SELECT * FROM Users WHERE username = ? OR email = ?"
        cur.execute(query, (username, email))
        existing_user = cur.fetchone()

        if existing_user is None:
            
            # Hash password and insert new user record
            hashpass = generate_password_hash(password)
            cur.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
                        (username, email, hashpass))
            db.commit()
            session['userID'] = username
            
            send_registration_email(username, email)

            return session['username']
        
        else:
            return False
    else:
        return False

def verify_reset_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt=security_salt , max_age=expiration)
    except Exception:
        return None
    return email

def recover_user(form):
    username = form.username.data
    email = form.email.data
        
    print(f"A recovery attempt for account: {username} and email: {email} was attempted.")
            
    db = get_database()
    cur = db.cursor()

    query = 'SELECT * FROM Users WHERE username = ? COLLATE NOCASE AND email = ? COLLATE NOCASE'
    cur.execute(query, (username, email))
    existing_user = cur.fetchone()
    print(existing_user)

    if existing_user:
        x = "3600 Seconds"
        send_recovery_email(email, username)
        flash(f"Recovery Email Sent, Valid for {x}", "success")

        
        return redirect(url_for('index'))
    
    else:
        flash("Details incorrect", "danger")

        return redirect(url_for('recovery'))

def password_change(form):
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data 
        password2 = form.password2.data
        print(f'{username}, {password}, {password2}')

        if password == password2:
            print('password match attempting to hash')
            hashpass = generate_password_hash(password)
            
            print('accessing database')
            db = get_database()
            cur = db.cursor()

        # Check if user exists
            cur.execute("SELECT username FROM Users WHERE username = ?", (username,))
            print(f'username: {username} found in db')
            user = cur.fetchone()

        if user:
            cur.execute("""
                UPDATE Users
                SET password = ?
                WHERE username = ?
            """, (hashpass, username))
            db.commit()

            print(f"✅ Password updated for user '{username}' with '{hashpass}")
            return form
        else:
            print(f"⚠️ No user found with username: {username}")
            return False
    
    flash("password change aborted", "danger")
    return redirect(url_for('index'))