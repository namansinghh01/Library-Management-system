from flask import Flask, render_template, session, redirect, url_for, request
from config import Config
from sqlalchemy import text
from routes.students_routes import student_bp
from routes.authors_routes import author_bp
from routes.books_routes import book_bp
from routes.transactions_routes import transaction_bp
from routes.auth_routes import auth_bp
from routes.requests_routes import request_bp
from routes.wishlist_routes import wishlist_bp
from routes.reviews_routes import review_bp
from utils.decorators import login_required
from db import *
from models import *
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "super_secret_lms_key"  # Needed for flash messages
db.init_app(app)
migrate = Migrate(app,db)

@app.route("/db-health")
def db_health():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status":"ok", "database":"connected"}
    except Exception as e:
        return {"status": str(e)}

@app.route('/')
@login_required
def index():
    chart_labels = []
    chart_data = []

    if session.get('role') == 'admin':
        total_books = Book.query.count()
        total_students = Student.query.count()
        total_authors = Author.query.count()
        active_issues = Transaction.query.filter_by(status='issued').count()
        recent_transactions = Transaction.query.order_by(Transaction.issue_date.desc()).limit(5).all()
        
        category_counts = db.session.query(Book.category, db.func.count(Book.id)).group_by(Book.category).all()
        chart_labels = [c[0] if c[0] else 'Other' for c in category_counts]
        chart_data = [c[1] for c in category_counts]
    elif session.get('role') == 'author':
        total_books = Book.query.filter_by(author_id=session['user_id']).count()
        total_students = 0
        total_authors = 0
        active_issues = 0 # Future improvement
        recent_transactions = []
    elif session.get('role') == 'student':
        total_books = 0
        total_students = 0
        total_authors = 0
        active_issues = Transaction.query.filter_by(student_id=session['user_id'], status='issued').count()
        recent_transactions = Transaction.query.filter_by(student_id=session['user_id']).order_by(Transaction.issue_date.desc()).limit(5).all()
    
    return render_template('index.html',
                           total_books=total_books,
                           total_students=total_students,
                           total_authors=total_authors,
                           active_issues=active_issues,
                           recent_transactions=recent_transactions,
                           chart_labels=chart_labels,
                           chart_data=chart_data)

# Blueprint register
app.register_blueprint(student_bp,url_prefix="/student")
app.register_blueprint(author_bp,url_prefix="/author")
app.register_blueprint(book_bp,url_prefix="/book")
app.register_blueprint(transaction_bp, url_prefix="/transaction")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(request_bp, url_prefix="/requests")
app.register_blueprint(wishlist_bp, url_prefix="/wishlist")
app.register_blueprint(review_bp, url_prefix="/reviews")

@app.context_processor
def inject_notifications():
    if session.get('role') == 'student' and session.get('user_id'):
        from datetime import datetime
        student_id = session.get('user_id')
        
        # Get active unread persistent notifications (from database)
        db_notifs = Notification.query.filter_by(student_id=student_id, is_read=False).order_by(Notification.created_at.desc()).all()
        notifs_list = [{"id": n.id, "message": n.message, "type": "db"} for n in db_notifs]
        
        # Dynamically calculate "3 days left" notifications from transactions
        active_txs = Transaction.query.filter_by(student_id=student_id, status='issued').all()
        for tx in active_txs:
            if tx.due_date_calc:
                days_left = (tx.due_date_calc - datetime.utcnow()).days
                if 0 <= days_left <= 3:
                    notifs_list.append({
                        "id": f"tx_{tx.id}", 
                        "message": f"Reminder: Your book '{tx.book.title}' is due in {days_left} day(s).",
                        "type": "dynamic"
                    })
                elif days_left < 0:
                    notifs_list.append({
                        "id": f"tx_{tx.id}", 
                        "message": f"Alert: Your book '{tx.book.title}' is overdue! Please return it soon to avoid further fines.",
                        "type": "overdue"
                    })
                    
        return dict(user_notifications=notifs_list, unread_count=len(notifs_list))
    return dict(user_notifications=[], unread_count=0)

@app.route("/notifications/mark_read", methods=["POST"])
@login_required
def mark_read():
    if session.get('role') == 'student':
        # Mark all database notifications as read
        Notification.query.filter_by(student_id=session['user_id'], is_read=False).update({"is_read": True})
        db.session.commit()
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    # Auto-reload OTP functionality hit
    app.run(debug=True)