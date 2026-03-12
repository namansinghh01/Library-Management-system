from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from utils.decorators import login_required, role_required
from models import Author
from db import db
from utils.email_utils import send_registration_email, send_otp_email, send_otp_sms
import random

author_bp = Blueprint("author", __name__)

@author_bp.route("/")
@login_required
@role_required('admin')
def list_authors():
    authors = Author.query.all()
    return render_template("author/list.html", authors=authors)

@author_bp.route("/add", methods=["GET", "POST"])
def add_author(): # Serves as registration
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "send_otp":
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            bio = request.form.get("bio")
            otp_method = request.form.get("otp_method")
            
            otp = str(random.randint(100000, 999999))
            
            session['temp_author_data'] = {
                'name': name,
                'email': email,
                'password': password,
                'bio': bio,
                'otp': otp
            }
            
            if otp_method == 'phone':
                # Actually Authors only prompt for email in their registration right now, let's gracefully fallback if they select phone
                send_otp_sms("Unknown Phone", otp)
                flash(f"OTP sent via SIMULATED SMS.", "info")
            else:
                send_otp_email(email, otp)
                flash(f"OTP sent successfully to Email: {email}", "info")
                
            return render_template("author/add.html", step="verify")
            
        elif action == "verify_otp":
            entered_otp = request.form.get("otp")
            temp_data = session.get('temp_author_data')
            
            if not temp_data:
                flash("Session expired or invalid. Please try registering again.", "error")
                return redirect(url_for('author.add_author'))
                
            if temp_data['otp'] == entered_otp:
                # OTP matched! Complete registration
                hashed_pw = generate_password_hash(temp_data['password'])
                new_author = Author(
                    name=temp_data['name'], 
                    email=temp_data['email'], 
                    password_hash=hashed_pw, 
                    bio=temp_data['bio']
                )
                db.session.add(new_author)
                db.session.commit()
                
                # Send welcome email asynchronously
                send_registration_email(temp_data['email'], temp_data['name'], "author")
                
                # Clear session
                session.pop('temp_author_data', None)
                
                flash("Author registered successfully! Please login.", "success")
                return redirect(url_for('auth.login'))
            else:
                flash("Invalid OTP entered. Please try again.", "error")
                return render_template("author/add.html", step="verify")
        
    return render_template("author/add.html", step="details")

@author_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@role_required('admin')
def delete_author(id):
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    flash("Author deleted successfully!", "success")
    return redirect(url_for('author.list_authors'))