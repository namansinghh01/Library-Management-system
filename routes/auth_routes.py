from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from models import Student, Author, Admin
from db import db
from utils.decorators import login_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_or_username = request.form.get("email")
        password = request.form.get("password")
        role_type = request.form.get("role_type")
        
        if role_type == "admin":
            user = Admin.query.filter_by(username=email_or_username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['role'] = 'admin'
                session['profile_pic'] = getattr(user, 'profile_pic', None)
                flash("Logged in successfully as Admin!", "success")
                return redirect(url_for('index'))
                
        elif role_type == "author":
            user = Author.query.filter_by(email=email_or_username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['role'] = 'author'
                session['user_name'] = user.name
                session['profile_pic'] = getattr(user, 'profile_pic', None)
                flash("Logged in successfully as Author!", "success")
                return redirect(url_for('index'))
                
        elif role_type == "student":
            user = Student.query.filter_by(stu_email=email_or_username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['role'] = 'student'
                session['user_name'] = user.stu_name
                session['profile_pic'] = getattr(user, 'profile_pic', None)
                flash("Logged in successfully as Student!", "success")
                return redirect(url_for('index'))
                
        flash("Invalid credentials or role.", "error")
        return redirect(url_for('auth.login'))
        
    return render_template("auth/login.html")

@auth_bp.route("/setup_admin")
def setup_admin():
    # Only for initial setup, creates admin if it doesn't exist
    if Admin.query.count() == 0:
        admin = Admin(username="admin", password_hash=generate_password_hash("admin123"))
        db.session.add(admin)
        db.session.commit()
        return "Admin user created (admin / admin123). Please go to /login"
    return "Admin already exists! Go to /login"

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route("/upload_profile_pic", methods=["POST"])
@login_required
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        flash("No file part", "error")
        return redirect(request.referrer or url_for('index'))
    file = request.files['profile_pic']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(request.referrer or url_for('index'))
    if file:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        new_filename = f"{session['role']}_{session['user_id']}_{uuid.uuid4().hex}.{ext}" if ext else f"{session['role']}_{session['user_id']}_{uuid.uuid4().hex}"
        
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, new_filename))
        
        role = session.get('role')
        user_id = session.get('user_id')
        user = None
        if role == 'admin':
            user = Admin.query.get(user_id)
        elif role == 'author':
            user = Author.query.get(user_id)
        elif role == 'student':
            user = Student.query.get(user_id)
            
        if user:
            # Remove old profile picture if exists
            if user.profile_pic and user.profile_pic != 'default.jpg':
                old_pic_path = os.path.join(upload_path, user.profile_pic)
                if os.path.exists(old_pic_path):
                    try:
                        os.remove(old_pic_path)
                    except Exception:
                        pass
                        
            user.profile_pic = new_filename
            db.session.commit()
            session['profile_pic'] = new_filename
            flash("Profile picture updated successfully!", "success")
            
    return redirect(request.referrer or url_for('index'))

@auth_bp.route("/remove_profile_pic", methods=["POST"])
@login_required
def remove_profile_pic():
    role = session.get('role')
    user_id = session.get('user_id')
    user = None
    
    if role == 'admin':
        user = Admin.query.get(user_id)
    elif role == 'author':
        user = Author.query.get(user_id)
    elif role == 'student':
        user = Student.query.get(user_id)
        
    if user and user.profile_pic and user.profile_pic != 'default.jpg':
        old_pic_path = os.path.join(current_app.root_path, 'static', 'uploads', user.profile_pic)
        if os.path.exists(old_pic_path):
            try:
                os.remove(old_pic_path)
            except Exception:
                pass
                
        user.profile_pic = 'default.jpg'
        db.session.commit()
        session['profile_pic'] = 'default.jpg'
        flash("Profile picture removed successfully!", "success")
        
    return redirect(request.referrer or url_for('auth.profile'))

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        if not old_password or not new_password or not confirm_password:
            flash("All fields are required.", "error")
            return redirect(url_for('auth.profile'))
            
        if new_password != confirm_password:
            flash("New passwords do not match.", "error")
            return redirect(url_for('auth.profile'))
            
        user_id = session.get('user_id')
        role = session.get('role')
        
        user = None
        if role == 'admin':
            user = Admin.query.get(user_id)
        elif role == 'author':
            user = Author.query.get(user_id)
        elif role == 'student':
            user = Student.query.get(user_id)
            
        if user and check_password_hash(user.password_hash, old_password):
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash("Password updated successfully!", "success")
        else:
            flash("Incorrect old password.", "error")
            
        return redirect(url_for('auth.profile'))
            
    return render_template("auth/profile.html")
