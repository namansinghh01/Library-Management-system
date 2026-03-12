from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from utils.decorators import login_required, role_required
from models import Student
from db import db
from utils.email_utils import send_registration_email, send_otp_email, send_otp_sms
import random

student_bp = Blueprint("student", __name__)

@student_bp.route("/")
@login_required
@role_required('admin')
def list_students():
    students = Student.query.all()
    return render_template("students/list.html", students=students)

@student_bp.route("/add", methods=["GET", "POST"])
def add_student(): # Registration
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "send_otp":
            full_name = request.form.get("full_name")
            email = request.form.get("email")
            password = request.form.get("password")
            number = request.form.get("phone")
            age = request.form.get("age")
            otp_method = request.form.get("otp_method") # 'email' or 'phone'
            
            # Use a secure random 6 digit OTP
            otp = str(random.randint(100000, 999999))
            
            # Save data temporarily in session
            session['temp_reg_data'] = {
                'full_name': full_name,
                'email': email,
                'password': password,
                'phone': number,
                'age': age,
                'otp': otp
            }
            
            if otp_method == 'phone':
                send_otp_sms(number, otp)
                flash(f"OTP sent directly to Phone: {number} (Check server console for simulated SMS)", "info")
            else:
                send_otp_email(email, otp)
                flash(f"OTP sent successfully to Email: {email}", "info")
                
            return render_template("students/add.html", step="verify")
            
        elif action == "verify_otp":
            entered_otp = request.form.get("otp")
            temp_data = session.get('temp_reg_data')
            
            if not temp_data:
                flash("Session expired or invalid. Please try registering again.", "error")
                return redirect(url_for('student.add_student'))
                
            if temp_data['otp'] == entered_otp:
                # OTP matched! Complete registration
                hashed_pw = generate_password_hash(temp_data['password'])
                new_student = Student(
                    stu_name=temp_data['full_name'], 
                    stu_email=temp_data['email'], 
                    password_hash=hashed_pw, 
                    stu_phone=temp_data['phone'], 
                    stu_age=temp_data['age']
                )
                db.session.add(new_student)
                db.session.commit()
                
                # Send welcome email asynchronously
                send_registration_email(temp_data['email'], temp_data['full_name'], "student")
                
                # Clear session data
                session.pop('temp_reg_data', None)
                
                flash("Student registered successfully! Please login.", "success")
                return redirect(url_for('auth.login'))
            else:
                flash("Invalid OTP entered. Please try again.", "error")
                return render_template("students/add.html", step="verify")
                
    return render_template("students/add.html", step="details")

@student_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@role_required('admin')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully!", "success")
    return redirect(url_for('student.list_students'))