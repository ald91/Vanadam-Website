#external modules
from flask import Blueprint, render_template, redirect, url_for, flash, request, session

#python modules
from functools import wraps

#self module
from . import auth
from .services import *

#app imports
from forms import LoginForm, RegisterForm, RecoveryForm, PasswordResetForm

##################
#-----Routes-----#
##################

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # If already logged in, do not show login page (commented out request.method =="GET" and)
    if 'username' in session:
        flash("Cannot log in while already logged in.", "error")
        return redirect(url_for('index'))

    # Handle Login
    if request.method == "POST":
        if log_in_user(form):
            flash(f"Logged in as {session['username']}", "success")
            return redirect(url_for('index'))
        else:
            flash("Incorrect username or password.", "error")
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('logged_in', None)

    flash("You’ve been logged out.", "info")
    return redirect(url_for('index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm()

    if request.method == "GET" and 'username' in session:
            print("Already logged in")
            flash("Cannot register a new account while already logged in.", "error")   
            return redirect(url_for('index'))
    
    if request.method == "POST":
        if register_user(form): # Retrieve inputs from form
            flash("Registration Successful", "success")          
            return redirect(url_for('index'))
        
        else:    
            flash("Credentials already taken", "error")
            return redirect(url_for('register'))
        
    return render_template('register.html', form=form)


@auth.route('/recovery', methods=['GET', 'POST'])
def recovery():
    form = RecoveryForm()

    if request.method == "GET":  
            return render_template('recovery.html', form=form)
    
    if request.method == "POST":
        if form.validate_on_submit():
            recover_user(form)
            return redirect(url_for('index'))
           
    return render_template('home.html')


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    
    form = PasswordResetForm()

    if request.method == 'GET':
        return render_template('reset_password.html', token=token, form=form)
    
    elif request.method == 'POST':
        if password_change(form):
            log_in_user(form)
            flash(f"password changed successfully. Logged in as {form.username.data}")
            return redirect(url_for('index'))
    else:
        flash('A recovery error has occured', 'error')
        return render_template('siteerror.html')


