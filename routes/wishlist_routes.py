from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, role_required
from models import Wishlist, Book
from db import db

wishlist_bp = Blueprint("wishlist", __name__)

@wishlist_bp.route("/")
@login_required
@role_required('student')
def list_wishlist():
    wishlists = Wishlist.query.filter_by(student_id=session['user_id']).order_by(Wishlist.added_date.desc()).all()
    return render_template("wishlist/list.html", wishlists=wishlists)

@wishlist_bp.route("/add/<int:book_id>", methods=["POST"])
@login_required
@role_required('student')
def add_to_wishlist(book_id):
    book = Book.query.get_or_404(book_id)
    existing = Wishlist.query.filter_by(student_id=session['user_id'], book_id=book_id).first()
    
    if existing:
        flash("Book is already in your wishlist.", "error")
    else:
        new_item = Wishlist(student_id=session['user_id'], book_id=book_id)
        db.session.add(new_item)
        db.session.commit()
        flash("Book added to wishlist!", "success")
        
    return redirect(request.referrer or url_for('book.list_books'))

@wishlist_bp.route("/remove/<int:id>", methods=["POST"])
@login_required
@role_required('student')
def remove_from_wishlist(id):
    item = Wishlist.query.get_or_404(id)
    if item.student_id == session['user_id']:
        db.session.delete(item)
        db.session.commit()
        flash("Book removed from wishlist.", "success")
    return redirect(request.referrer or url_for('wishlist.list_wishlist'))
