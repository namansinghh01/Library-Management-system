from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, role_required
from models import BookRequest, Book, Notification
from db import db

request_bp = Blueprint("requests", __name__)

@request_bp.route("/")
@login_required
@role_required('admin', 'student')
def list_requests():
    if session.get('role') == 'student':
        requests_list = BookRequest.query.filter_by(student_id=session['user_id']).order_by(BookRequest.request_date.desc()).all()
    else:
        requests_list = BookRequest.query.order_by(BookRequest.request_date.desc()).all()
    return render_template("requests/list.html", requests=requests_list)

@request_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required('student')
def add_request():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        
        if not title:
            flash("Title is required.", "error")
            return redirect(url_for('requests.add_request'))
            
        new_request = BookRequest(student_id=session['user_id'], title=title, author=author)
        db.session.add(new_request)
        db.session.commit()
        flash("New book request submitted successfully!", "success")
        return redirect(url_for('requests.list_requests'))
        
    return render_template("requests/add.html")

@request_bp.route("/request_existing/<int:book_id>", methods=["POST"])
@login_required
@role_required('student')
def request_existing(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Check if already requested and pending
    existing = BookRequest.query.filter_by(student_id=session['user_id'], book_id=book_id, status='pending').first()
    if existing:
        flash("You have already requested this book.", "error")
    else:
        new_request = BookRequest(student_id=session['user_id'], book_id=book_id)
        db.session.add(new_request)
        db.session.commit()
        flash("Book request sent to admin!", "success")
        
    return redirect(url_for('book.list_books'))

@request_bp.route("/update_status/<int:req_id>", methods=["POST"])
@login_required
@role_required('admin')
def update_status(req_id):
    req = BookRequest.query.get_or_404(req_id)
    status = request.form.get("status")
    if status in ['approved', 'rejected']:
        req.status = status
        
        # Determine book name based on if it's existing or new
        book_title = req.book.title if req.book_id else req.title
        
        # Create a notification for the student
        message = f"Your request for '{book_title}' has been {status}."
        notif = Notification(student_id=req.student_id, message=message)
        db.session.add(notif)
        
        db.session.commit()
        flash(f"Request marked as {status}!", "success")
    return redirect(url_for('requests.list_requests'))

@request_bp.route("/delete/<int:req_id>", methods=["POST"])
@login_required
@role_required('admin')
def delete_request(req_id):
    req = BookRequest.query.get_or_404(req_id)
    db.session.delete(req)
    db.session.commit()
    flash("Request record deleted successfully!", "success")
    return redirect(url_for('requests.list_requests'))
