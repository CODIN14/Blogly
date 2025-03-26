from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import requests  # Add this import for reCAPTCHA validation

authentication = Blueprint("authentication", __name__)

# reCAPTCHA Secret Key
RECAPTCHA_SECRET_KEY = '6Lf41v4qAAAAAA3QkItiyOV3saLqNIt53YTEDYH1'  # Replace with your reCAPTCHA Secret Key

@authentication.route("/login", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        # Get the reCAPTCHA response from the form
        recaptcha_response = request.form.get('g-recaptcha-response')

        # Verify reCAPTCHA with Google's API
        if not recaptcha_response:
            flash('Please complete the reCAPTCHA to proceed.', category='error')
            return render_template("login.html", user=current_user)

        # Send a request to Google's reCAPTCHA API to verify the response
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
            'remoteip': request.remote_addr
        }
        response = requests.post(verify_url, data=payload)
        result = response.json()

        # Check if reCAPTCHA verification was successful
        if not result.get('success'):
            flash('reCAPTCHA verification failed. Please try again.', category='error')
            return render_template("login.html", user=current_user)

        # Proceed with login if reCAPTCHA is valid
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect', category='error')
        else:
            flash('Email does not exist', category='error')
    return render_template("login.html", user=current_user)

@authentication.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        profile_picture = request.files.get("profile_picture")

        email_exist = User.query.filter_by(email=email).first()
        user_exist = User.query.filter_by(username=username).first()

        if email_exist:
            flash('Email already exists', category='error')
        elif user_exist:
            flash('Username already exists', category='error')
        elif password != confirm_password:
            flash('Passwords do not match', category='error')
        elif len(username) < 3:
            flash('Username is too short', category='error')
        elif len(password) < 6:
            flash('Password is too short', category='error')
        elif len(email) < 4:
            flash("Email is invalid", category='error')
        else:
            profile_picture_filename = None
            if profile_picture and profile_picture.filename:
                profile_picture_filename = secure_filename(profile_picture.filename)
                uploads_dir = os.path.join('applicaton', 'static', 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                profile_picture.save(os.path.join(uploads_dir, profile_picture_filename))

            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(password, method='pbkdf2:sha256'),
                profile_picture=profile_picture_filename
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("signup.html", user=current_user)

@authentication.route("/logout")
@login_required
def log_out():
    logout_user()
    return redirect(url_for("views.home"))

@authentication.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        user_exist = User.query.filter_by(username=new_username).first()
        if user_exist and user_exist != current_user:
            flash("Sorry, that username is already taken", category='error')
            return render_template("settings.html", user=current_user)
        if new_password != confirm_password:
            flash("Passwords do not match, please try again.", category='error')
            return render_template("settings.html", user=current_user)
        if len(new_username) < 3:
            flash('Username is too short', category='error')
            return render_template("settings.html", user=current_user)
        if len(new_password) < 6:
            flash('Password is too short', category='error')
            return render_template("settings.html", user=current_user)
        
        current_user.username = new_username
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()

        flash("Your settings have been updated!", category='success')
        return redirect(url_for('views.home'))
    return render_template("settings.html", user=current_user)