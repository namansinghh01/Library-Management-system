from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, role_required
from models import Book, Author, Wishlist
from db import db

book_bp = Blueprint("book", __name__)

@book_bp.route("/")
@login_required
@role_required('admin', 'author', 'student')
def list_books():
    category_filter = request.args.get('category')
    
    query = Book.query
    if session.get('role') == 'author':
        query = query.filter_by(author_id=session['user_id'])
        
    if category_filter:
        query = query.filter_by(category=category_filter)
        
    books = query.all()
    
    # Get unique categories for filter dropdown
    categories = db.session.query(Book.category).filter(Book.category.isnot(None)).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    user_wishlist = []
    if session.get('role') == 'student':
        wishlists = Wishlist.query.filter_by(student_id=session['user_id']).all()
        user_wishlist = [w.book_id for w in wishlists]
        
    # Calculate avg ratings for books
    book_ratings = {}
    for b in books:
        if b.reviews:
            avg = sum([r.rating for r in b.reviews]) / len(b.reviews)
            book_ratings[b.id] = (round(avg, 1), len(b.reviews))
        else:
            book_ratings[b.id] = (0, 0)
    
    return render_template("books/list.html", books=books, categories=categories, current_category=category_filter, user_wishlist=user_wishlist, book_ratings=book_ratings)

@book_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required('admin', 'author')
def add_book():
    if request.method == "POST":
        title = request.form.get("title")
        isbn = request.form.get("isbn")
        
        # If author, enforce their own ID. If admin, they can select.
        if session.get('role') == 'author':
            author_id = session['user_id']
        else:
            author_id = request.form.get("author_id")
            
        total_copies = int(request.form.get("total_copies", 1))
        category = request.form.get("category", "")
        
        new_book = Book(title=title, isbn=isbn, author_id=author_id, total_copies=total_copies, available_copies=total_copies, category=category)
        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully!", "success")
        return redirect(url_for('book.list_books'))
        
    authors = Author.query.all()
    return render_template("books/add.html", authors=authors)

@book_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@role_required('admin', 'author')
def delete_book(id):
    book = Book.query.get_or_404(id)
    if session.get('role') == 'author' and book.author_id != session['user_id']:
        flash("You can only delete your own books.", "error")
        return redirect(url_for('book.list_books'))
        
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully!", "success")
    return redirect(url_for('book.list_books'))