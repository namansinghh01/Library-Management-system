from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, role_required
from models import Transaction, Book, Student, Review
from db import db
from datetime import datetime

transaction_bp = Blueprint("transactions", __name__)

@transaction_bp.route("/")
@login_required
@role_required('admin', 'student')
def list_transactions():
    user_reviews = {}
    if session.get('role') == 'student':
        transactions = Transaction.query.filter_by(student_id=session['user_id']).order_by(Transaction.issue_date.desc()).all()
        # Create a dict of book_id -> review to color the stars in UI
        reviews = Review.query.filter_by(student_id=session['user_id']).all()
        user_reviews = {r.book_id: r for r in reviews}
    else:
        transactions = Transaction.query.order_by(Transaction.issue_date.desc()).all()
    return render_template("transactions/list.html", transactions=transactions, datetime=datetime, user_reviews=user_reviews)

@transaction_bp.route("/issue", methods=["GET", "POST"])
@login_required
@role_required('admin', 'student')
def issue_book():
    if request.method == "POST":
        if session.get('role') == 'student':
            student_id = session['user_id']
        else:
            student_id = request.form.get("student_id")
            
        book_id = request.form.get("book_id")
        
        book = Book.query.get(book_id)
        if book and book.available_copies > 0:
            transaction = Transaction(student_id=student_id, book_id=book_id, status='issued')
            book.available_copies -= 1
            db.session.add(transaction)
            db.session.commit()
            flash("Book issued successfully!", "success")
            return redirect(url_for('transactions.list_transactions'))
        else:
            flash("Book not available!", "error")
            return redirect(url_for('transactions.issue_book'))
            
    students = Student.query.all()
    books = Book.query.filter(Book.available_copies > 0).all()
    return render_template("transactions/issue.html", students=students, books=books)

@transaction_bp.route("/return/<int:tx_id>", methods=["POST"])
@login_required
@role_required('admin', 'student')
def return_book(tx_id):
    transaction = Transaction.query.get_or_404(tx_id)
    if session.get('role') == 'student' and transaction.student_id != session['user_id']:
        flash("You can only return your own books.", "error")
        return redirect(url_for('transactions.list_transactions'))
        
    if transaction.status == 'issued':
        transaction.status = 'returned'
        transaction.return_date = datetime.utcnow()
        transaction.book.available_copies += 1
        db.session.commit()
        flash("Book returned successfully!", "success")
    return redirect(url_for('transactions.list_transactions'))

@transaction_bp.route("/delete/<int:tx_id>", methods=["POST"])
@login_required
@role_required('admin')
def delete_transaction(tx_id):
    transaction = Transaction.query.get_or_404(tx_id)
    db.session.delete(transaction)
    db.session.commit()
    flash("Transaction record deleted successfully!", "success")
    return redirect(url_for('transactions.list_transactions'))
