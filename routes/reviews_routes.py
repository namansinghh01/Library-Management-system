from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from utils.decorators import login_required, role_required
from models import Review, Transaction, Book
from db import db

review_bp = Blueprint("reviews", __name__)

@review_bp.route("/")
@login_required
@role_required('admin', 'author')
def list_reviews():
    if session.get('role') == 'admin':
        reviews = Review.query.order_by(Review.created_at.desc()).all()
    else:
        # Author can only see reviews for their own books
        reviews = Review.query.join(Book).filter(Book.author_id == session['user_id']).order_by(Review.created_at.desc()).all()
        
    return render_template("reviews/list.html", reviews=reviews)

@review_bp.route("/add/<int:book_id>", methods=["POST"])
@login_required
@role_required('student')
def add_review(book_id):
    rating = request.form.get("rating")
    comment = request.form.get("comment", "").strip()
    
    if not rating or not str(rating).isdigit() or not (1 <= int(rating) <= 5):
        flash("Please provide a valid star rating (1-5).", "error")
        return redirect(request.referrer or url_for('transactions.list_transactions'))
        
    rating = int(rating)
    
    # Check if this student actually issued and returned this book at some point
    has_returned = Transaction.query.filter_by(student_id=session['user_id'], book_id=book_id, status='returned').first()
    if not has_returned:
        flash("You can only review books you have returned.", "error")
        return redirect(request.referrer or url_for('transactions.list_transactions'))
        
    # Check if a review already exists
    existing = Review.query.filter_by(student_id=session['user_id'], book_id=book_id).first()
    
    if existing:
        existing.rating = rating
        existing.comment = comment
        flash("Your review was updated!", "success")
    else:
        new_review = Review(student_id=session['user_id'], book_id=book_id, rating=rating, comment=comment)
        db.session.add(new_review)
        flash("Thank you! Your review was submitted.", "success")
        
    db.session.commit()
    return redirect(request.referrer or url_for('transactions.list_transactions'))
